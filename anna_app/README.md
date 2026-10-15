# Task Manager — Anna App

An Anna app for managing tasks through an authenticated Django REST API.

## Features

- List tasks for the authenticated user.
- Create tasks with a title, description, and priority.
- Summarize task status and overdue work.
- Generate a daily task plan.
- Check plugin availability with ping.

## Configuration

Set DJANGO_API_URL to your Django API base URL, ending in /api.
Set DJANGO_API_TOKEN to a valid private authentication token.

Default API URL: https://ai-task-management-agent.onrender.com/api

Never commit tokens, passwords, or .env files. Keep credentials private.

## Local validation

Run these commands from the anna_app directory:

    anna-app validate
    anna-app validate --strict

Run Executa tests from anna_app/executas/task-manager.

Task creation writes to the configured API, so use labelled test tasks when testing against production.

Local validation does not guarantee publication approval or payment eligibility.
