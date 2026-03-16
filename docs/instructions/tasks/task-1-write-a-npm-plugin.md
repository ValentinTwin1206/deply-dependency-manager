# Task 1: Write a Third-Party NPM Plugin

## Task

With the [DevContainer environment set up](../getting-started/getting-started.md), `depsight` is available directly from the command line:

![Depsight CLI](../../images/depsight_cli.png)

Your first task is to implement an **NPM plugin for Depsight** that exposes a `depsight npm scan` command. Completing this task is a prerequisite for [Task 2](task-2-scan-dependencies.md), where you will use your plugin to run a full dependency scan on the `package.json` of the target ['fancy-fileserver'](https://github.com/ValentinTwin1206/fancy-fileserver) project and report its dependencies.

!!! info "Fancy Fileserver Already Packaged"
    The `fancy-fileserver` repository is already available inside the DevContainer environment under `~/fancy-fileserver`.

### Excursus: NPM Dependencies

An NPM project declares its dependencies in `package.json` under two keys:

- **`dependencies`** — packages required at runtime.
- **`devDependencies`** — packages needed only during development (e.g., testing, linting).

Each key maps package names to version strings:

```json
{
  "dependencies": {
    "ajv": "^8.17.1",
    "bcrypt": "^5.1.0",
    "fastify": "^4.23.0"
  },
  "devDependencies": {
    "artillery": "^2.0.28",
    "bun-types": "^1.3.0",
    "playwright": "^1.58.0"
  }
}
```

> NPM also uses files like `package-lock.json` and `.npmrc`, but for this task we focus exclusively on `package.json`.

## Hints

### Inline TODOs

The template repository already provides the plumbing required to run a working **"Hello World" plugin**. Thus, you do not need to set up the plugin structure from scratch; however, you are free to add additional Python modules to keep the architecture clean.

The DevContainer comes with the [Todo Tree](https://marketplace.visualstudio.com/items?itemName=Gruntfuggly.todo-tree) extension pre-installed. It scans your workspace for inline `# TODO` comments and displays them in a structured tree view, giving you a clear overview of every step that still needs to be implemented.

![Todos Overview](../../images/todos_task_1.png)

Throughout the plugin source code you will find a series of `# TODO` comments. Each one marks a specific step you need to complete in order to implement a fully working NPM plugin. Simply follow the TODOs since they guide you through reading `package.json`, collecting dependencies, and wiring up the `depsight npm scan` command.

!!! warning "Skip the `build.yml` and `Dockerfile`"
    Implement all TODOs **except** the one inside the `Dockerfile` and `.github/workflows/build.yml`. That TODO is covered in [Task 3](task-3-package-and-publish-your-plugin.md).
