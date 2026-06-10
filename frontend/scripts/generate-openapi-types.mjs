import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const frontendRoot = resolve(__dirname, "..");
const repoRoot = resolve(frontendRoot, "..");
const backendRoot = resolve(repoRoot, "backend");
const outputDir = resolve(frontendRoot, "src/types/generated");
const schemaPath = resolve(outputDir, "openapi-schema.json");
const typesPath = resolve(outputDir, "openapi.ts");
const pythonBin =
  process.env.PYTHON_BIN ??
  (existsSync("/opt/miniconda3/bin/python3") ? "/opt/miniconda3/bin/python3" : "python3");

const openApiProcess = spawnSync(
  pythonBin,
  [
    "-c",
    [
      "import json",
      "from app.main import app",
      "print(json.dumps(app.openapi(), sort_keys=True))"
    ].join("; ")
  ],
  {
    cwd: repoRoot,
    env: {
      ...process.env,
      PYTHONPATH: [backendRoot, process.env.PYTHONPATH].filter(Boolean).join(":"),
      DATABASE_URL: "sqlite+pysqlite:///:memory:",
      ENVIRONMENT: "test"
    },
    encoding: "utf-8"
  }
);

if (openApiProcess.status !== 0) {
  process.stderr.write(openApiProcess.stderr);
  process.exit(openApiProcess.status ?? 1);
}

const schema = JSON.parse(openApiProcess.stdout);
mkdirSync(outputDir, { recursive: true });
writeFileSync(schemaPath, `${JSON.stringify(schema, null, 2)}\n`);
writeFileSync(typesPath, renderTypes(schema));

function renderTypes(openApiSchema) {
  const schemas = openApiSchema.components?.schemas ?? {};
  const schemaEntries = Object.entries(schemas)
    .map(([name, value]) => `    ${JSON.stringify(name)}: ${renderSchema(value)};`)
    .join("\n");
  const pathEntries = Object.entries(openApiSchema.paths ?? {})
    .map(([path, value]) => `  ${JSON.stringify(path)}: ${renderPathItem(value)};`)
    .join("\n");

  return `/* eslint-disable */\n/* tslint:disable */\n// This file is generated from the backend OpenAPI schema.\n// Run npm run generate:api-types from frontend/ to regenerate.\n\nexport interface components {\n  schemas: {\n${schemaEntries}\n  };\n}\n\nexport interface paths {\n${pathEntries}\n}\n`;
}

function renderPathItem(pathItem) {
  const methods = ["get", "post", "put", "patch", "delete"];
  const entries = methods
    .filter((method) => pathItem[method])
    .map((method) => `    ${method}: ${renderOperation(pathItem[method])};`)
    .join("\n");
  return `{\n${entries}\n  }`;
}

function renderOperation(operation) {
  const requestSchema =
    operation.requestBody?.content?.["application/json"]?.schema ??
    operation.requestBody?.content?.["application/x-www-form-urlencoded"]?.schema;
  const responseEntries = Object.entries(operation.responses ?? {})
    .map(([status, response]) => {
      const schema = response?.content?.["application/json"]?.schema;
      return `      ${JSON.stringify(status)}: ${schema ? renderSchema(schema) : "unknown"};`;
    })
    .join("\n");
  const parameters = operation.parameters?.length
    ? renderParameters(operation.parameters)
    : "Record<string, never>";

  return `{\n      parameters: ${parameters};\n      requestBody: ${requestSchema ? renderSchema(requestSchema) : "never"};\n      responses: {\n${responseEntries}\n      };\n    }`;
}

function renderParameters(parameters) {
  const grouped = parameters.reduce((acc, parameter) => {
    acc[parameter.in] ??= [];
    acc[parameter.in].push(parameter);
    return acc;
  }, {});
  const groups = Object.entries(grouped)
    .map(([location, items]) => {
      const properties = items
        .map((parameter) => {
          const optional = parameter.required ? "" : "?";
          return `        ${JSON.stringify(parameter.name)}${optional}: ${renderSchema(parameter.schema)};`;
        })
        .join("\n");
      return `      ${location}: {\n${properties}\n      };`;
    })
    .join("\n");
  return `{\n${groups}\n    }`;
}

function renderSchema(schema) {
  if (!schema) {
    return "unknown";
  }
  if (schema.$ref) {
    return renderRef(schema.$ref);
  }
  if (schema.enum) {
    return schema.enum.map((value) => JSON.stringify(value)).join(" | ");
  }
  if (schema.anyOf) {
    return schema.anyOf.map(renderSchema).join(" | ");
  }
  if (schema.oneOf) {
    return schema.oneOf.map(renderSchema).join(" | ");
  }
  if (schema.allOf) {
    return schema.allOf.map(renderSchema).join(" & ");
  }
  if (schema.type === "array") {
    const itemType = renderSchema(schema.items);
    return `${itemType.includes(" | ") || itemType.includes(" & ") ? `(${itemType})` : itemType}[]`;
  }
  if (schema.type === "object" || schema.properties) {
    return renderObject(schema);
  }
  if (schema.type === "string") {
    return "string";
  }
  if (schema.type === "integer" || schema.type === "number") {
    return "number";
  }
  if (schema.type === "boolean") {
    return "boolean";
  }
  if (schema.type === "null") {
    return "null";
  }
  return "unknown";
}

function renderObject(schema) {
  if (!schema.properties && schema.additionalProperties) {
    const additional =
      schema.additionalProperties === true ? "unknown" : renderSchema(schema.additionalProperties);
    return `Record<string, ${additional}>`;
  }
  const required = new Set(schema.required ?? []);
  const properties = Object.entries(schema.properties ?? {})
    .map(([name, value]) => {
      const optional = required.has(name) ? "" : "?";
      return `      ${JSON.stringify(name)}${optional}: ${renderSchema(value)};`;
    })
    .join("\n");
  return `{\n${properties}\n    }`;
}

function renderRef(ref) {
  const name = ref.split("/").at(-1);
  return `components["schemas"][${JSON.stringify(name)}]`;
}
