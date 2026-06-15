#!/usr/bin/env node
'use strict';

const gitbook = require('gitbook');

const commands = gitbook.commands.filter((command) => command.name.split(' ')[0] !== 'init');
const commandName = process.argv[2] || 'help';

function coerceValue(value) {
    if (value === 'true') return true;
    if (value === 'false') return false;
    if (/^\d+$/.test(value)) return Number(value);
    return value;
}

function parseArgs(argv) {
    const args = [];
    const kwargs = {};

    for (let i = 0; i < argv.length; i += 1) {
        const token = argv[i];

        if (token.indexOf('--no-') === 0) {
            kwargs[token.slice(5)] = false;
            continue;
        }

        if (token.indexOf('--') === 0) {
            const raw = token.slice(2);
            const equalIndex = raw.indexOf('=');

            if (equalIndex !== -1) {
                kwargs[raw.slice(0, equalIndex)] = coerceValue(raw.slice(equalIndex + 1));
                continue;
            }

            if (argv[i + 1] && argv[i + 1].indexOf('-') !== 0) {
                kwargs[raw] = coerceValue(argv[i + 1]);
                i += 1;
            } else {
                kwargs[raw] = true;
            }

            continue;
        }

        args.push(token);
    }

    return { args, kwargs };
}

function getCommand(name) {
    return commands.find((command) => command.name.split(' ')[0] === name);
}

function printHelp() {
    commands.forEach((command) => {
        console.log(`    ${command.name.padEnd(28)}${command.description}`);
    });
}

function applyDefaults(command, kwargs) {
    (command.options || []).forEach((option) => {
        if (kwargs[option.name] === undefined) {
            kwargs[option.name] = option.defaults;
        }

        if (option.values && option.values.indexOf(kwargs[option.name]) === -1) {
            throw new Error(`Invalid value for option "${option.name}"`);
        }
    });
}

function run() {
    if (commandName === 'help' || commandName === '--help' || commandName === '-h') {
        printHelp();
        return Promise.resolve();
    }

    const command = getCommand(commandName);
    if (!command) {
        throw new Error(`Command ${commandName} does not exist. Run "npm run gitbook -- help" to list commands.`);
    }

    const parsed = parseArgs(process.argv.slice(3));
    applyDefaults(command, parsed.kwargs);

    return Promise.resolve(command.exec(parsed.args, parsed.kwargs));
}

run().catch((error) => {
    console.error(error && error.stack ? error.stack : error);
    process.exitCode = 1;
});
