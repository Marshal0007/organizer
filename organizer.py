import click
import requests
import webbrowser
import os
import json
from requests.exceptions import RequestException
from fuzzywuzzy import fuzz
from colorama import Fore, Style, init
import pyfiglet  # Import pyfiglet

init(autoreset=True)

DEFAULT_DB_PATH = os.path.expanduser("~/.resource_db.json")


def load_resources(db_path):
    try:
        with open(db_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(
            Fore.RED
            + "Error: Invalid JSON in database file. Starting with an empty database."
            + Style.RESET_ALL
        )
        return {}


def save_resources(resources, db_path):
    try:
        with open(db_path, "w") as f:
            json.dump(resources, f, indent=4)
    except Exception as e:
        print(Fore.RED + f"Error saving resources to {db_path}: {e}" + Style.RESET_ALL)


def find_closest_match(resource_name, resources):
    names = [resource["name"].lower().strip() for resource in resources.values()]
    resource_name = resource_name.strip()

    if names:
        best_match = fuzz.ratio(resource_name.lower(), names[0])
        closest_name = names[0]

        for name in names[1:]:
            match = fuzz.ratio(resource_name.lower(), name)
            if match > best_match:
                best_match = match
                closest_name = name
        return closest_name
    return None


def display_banner():
    """Displays the tool's name in ASCII art and usage instructions."""
    ascii_banner = pyfiglet.figlet_format("ORGANIZER")
    click.echo(Fore.GREEN + ascii_banner + Style.RESET_ALL)
    click.echo(
        Fore.CYAN + "A tool to organize and manage project resources" + Style.RESET_ALL
    )
    click.echo(Fore.YELLOW + "\nUsage:" + Style.RESET_ALL)
    click.echo(
        Fore.WHITE
        + "  organizer add <name> <url> <description> <category>"
        + Style.RESET_ALL
    )
    click.echo(
        Fore.WHITE + "  organizer list [--category <category>]" + Style.RESET_ALL
    )
    click.echo(Fore.WHITE + "  organizer open <name>" + Style.RESET_ALL)
    click.echo(Fore.WHITE + "  organizer search <keyword>" + Style.RESET_ALL)
    click.echo(Fore.RED + "  organizer --help (for more information)" + Style.RESET_ALL)
    click.echo("\n")


@click.group()
@click.option(
    "--dbpath", default=DEFAULT_DB_PATH, help="Path to the resource database file"
)
@click.pass_context
def cli(ctx, dbpath):
    """Organize and manage your project resources."""
    ctx.ensure_object(dict)
    ctx.obj["dbpath"] = dbpath
    ctx.obj["resources"] = load_resources(dbpath)
    display_banner()  # Display the banner when the tool starts

    while True:  # Main command loop
        command = click.prompt(
            Fore.BLUE + "organizer> " + Style.RESET_ALL,
            type=str,
            default="help",
            show_default=False,
        )
        if command.lower() == "exit":
            break

        # Manually parse the command and arguments. This is needed since click is not designed to provide a "persistent shell" out of the box
        parts = command.split()
        if not parts:
            display_banner()  # If only prompt and then enter, show banner again
            continue

        command_name = parts[0].lower()
        command_args = parts[1:]

        if command_name == "add":
            if len(command_args) < 3:
                click.echo(
                    Fore.RED
                    + "Error: 'add' command requires name, description, and category."
                    + Style.RESET_ALL
                )
                continue
            name = command_args[0]
            url = command_args[1] if len(command_args) > 1 else None
            description = command_args[-2]
            category = command_args[-1]
            add_resource(ctx, name, url, description, category)

        elif command_name == "list":
            category = None
            if len(command_args) > 0 and command_args[0] == "--category":
                if len(command_args) > 1:
                    category = command_args[1]
                else:
                    click.echo(
                        Fore.RED
                        + "Error: '--category' option requires a value."
                        + Style.RESET_ALL
                    )
                    continue
            list_resource(ctx, category)

        elif command_name == "open":
            if len(command_args) != 1:
                click.echo(
                    Fore.RED
                    + "Error: 'open' command requires a resource name."
                    + Style.RESET_ALL
                )
                continue
            open_resource(ctx, command_args[0])

        elif command_name == "search":
            if len(command_args) != 1:
                click.echo(
                    Fore.RED
                    + "Error: 'search' command requires a keyword."
                    + Style.RESET_ALL
                )
                continue
            search_resource(ctx, command_args[0])

        elif command_name == "update":
            if len(command_args) < 1:
                click.echo(
                    Fore.RED
                    + "Error: 'update' command requires a resource name."
                    + Style.RESET_ALL
                )
                continue
            name = command_args[0]
            url = None
            description = None
            category = None

            i = 1
            while i < len(command_args):
                if command_args[i] == "--url" and i + 1 < len(command_args):
                    url = command_args[i + 1]
                    i += 2
                elif command_args[i] == "--description" and i + 1 < len(command_args):
                    description = command_args[i + 1]
                    i += 2
                elif command_args[i] == "--category" and i + 1 < len(command_args):
                    category = command_args[i + 1]
                    i += 2
                else:
                    click.echo(
                        Fore.RED
                        + f"Error: Invalid option '{command_args[i]}'"
                        + Style.RESET_ALL
                    )
                    break
            else:
                update_resource(ctx, name, url, description, category)
            continue  # Skip to the next iteration

        elif command_name == "delete":
            if len(command_args) != 1:
                click.echo(
                    Fore.RED
                    + "Error: 'delete' command requires a resource name."
                    + Style.RESET_ALL
                )
                continue
            delete_resource(ctx, command_args[0])

        elif command_name == "help":
            display_banner()

        else:
            click.echo(
                Fore.RED + f"Error: Unknown command '{command_name}'." + Style.RESET_ALL
            )


@cli.command(hidden=True)  # Hide the Click commands
@click.argument("name")
@click.argument("url", required=False)
@click.argument("description")
@click.argument("category")
@click.pass_context
def add_resource(ctx, name, url, description, category):
    """Add a new resource."""
    resources = ctx.obj["resources"]
    dbpath = ctx.obj["dbpath"]

    resource_id = name.lower().replace(" ", "_")
    if resource_id in resources:
        click.echo(
            Fore.RED + f"Error: Resource '{name}' already exists." + Style.RESET_ALL
        )
        return

    if url:
        try:
            response = requests.head(url, timeout=5)
            response.raise_for_status()
        except RequestException as e:
            click.echo(Fore.RED + f"Error: Invalid URL '{url}': {e}" + Style.RESET_ALL)
            return
    else:
        click.echo(
            Fore.YELLOW + "URL not provided. Skipping URL validation." + Style.RESET_ALL
        )

    resources[resource_id] = {
        "name": name,
        "url": url,
        "description": description,
        "category": category,
    }
    save_resources(resources, dbpath)
    click.echo(Fore.GREEN + f"Resource '{name}' added successfully." + Style.RESET_ALL)
    ctx.obj["resources"] = resources  # Update resources in context


@cli.command(hidden=True)  # Hide the Click commands
@click.option("--category", help="Filter resources by category")
@click.pass_context
def list_resource(ctx, category):
    """List resources, optionally filtered by category."""
    resources = ctx.obj["resources"]

    if category:
        filtered_resources = {
            k: v for k, v in resources.items() if v["category"] == category
        }
    else:
        filtered_resources = resources

    if not filtered_resources:
        click.echo(Fore.YELLOW + "No resources found." + Style.RESET_ALL)
        return

    click.echo(Fore.CYAN + "\nResources:" + Style.RESET_ALL)
    for resource_id, resource in filtered_resources.items():
        click.echo(
            Fore.MAGENTA
            + f"  - {resource['name']} ({resource['category']})"
            + Style.RESET_ALL
        )
        click.echo(
            Fore.WHITE
            + f"    URL: {resource['url'] if resource['url'] else 'N/A'}"
            + Style.RESET_ALL
        )
        click.echo(
            Fore.WHITE
            + f"    Description: {resource['description']}\n"
            + Style.RESET_ALL
        )


@cli.command(hidden=True)  # Hide the Click commands
@click.argument("name")
@click.pass_context
def open_resource(ctx, name):
    """Open a resource in your web browser."""
    resources = ctx.obj["resources"]
    search_term = name.lower()
    resource_id = search_term.replace(" ", "_")

    if resource_id in resources:
        resource = resources[resource_id]
        if resource["url"]:
            webbrowser.open_new_tab(resource["url"])
            click.echo(
                Fore.GREEN
                + f"Opening '{resource['name']}' in your browser."
                + Style.RESET_ALL
            )
        else:
            click.echo(
                Fore.YELLOW
                + f"Resource '{resource['name']}' exists but does not have a URL to open."
                + Style.RESET_ALL
            )
        return

    closest_match = find_closest_match(name, resources)
    if closest_match:
        click.echo(
            Fore.RED
            + f"Error: Resource '{name}' not found. Did you mean '{closest_match}'?"
            + Style.RESET_ALL
        )
        return

    click.echo(Fore.RED + f"Error: Resource '{name}' not found." + Style.RESET_ALL)


@cli.command(hidden=True)  # Hide the Click commands
@click.argument("keyword")
@click.pass_context
def search_resource(ctx, keyword):
    """Search resources by keyword in description."""
    resources = ctx.obj["resources"]
    keyword = keyword.lower()
    results = {}

    for resource_id, resource in resources.items():
        if keyword in resource["description"].lower():
            results[resource_id] = resource

    if not results:
        click.echo(
            Fore.YELLOW + f"No resources found matching '{keyword}'." + Style.RESET_ALL
        )
        return

    click.echo(Fore.CYAN + "\nSearch Results:" + Style.RESET_ALL)
    for resource_id, resource in results.items():
        click.echo(
            Fore.MAGENTA
            + f"  - {resource['name']} ({resource['category']})"
            + Style.RESET_ALL
        )
        click.echo(
            Fore.WHITE
            + f"    URL: {resource['url'] if resource['url'] else 'N/A'}"
            + Style.RESET_ALL
        )
        click.echo(
            Fore.WHITE
            + f"    Description: {resource['description']}\n"
            + Style.RESET_ALL
        )


@cli.command(hidden=True)
@click.argument("name")
@click.argument("url", required=False)
@click.argument("description", required=False)
@click.argument("category", required=False)
@click.pass_context
def update_resource(ctx, name, url, description, category):
    """Updates an existing resource."""
    resources = ctx.obj["resources"]
    dbpath = ctx.obj["dbpath"]
    resource_id = name.lower().replace(" ", "_")

    # Make the resource ID lookup case-insensitive
    resource_id_found = None
    for res_id in resources:
        if res_id.lower() == resource_id:
            resource_id_found = res_id
            break

    if resource_id_found is None:
        closest_match = find_closest_match(name, resources)
        error_message = f"Error: Resource '{name}' not found."
        if closest_match:
            error_message += f"  Did you mean '{closest_match}'?"
        click.echo(Fore.RED + error_message + Style.RESET_ALL)
        return

    # Update the resource if new data is provided
    if url:
        try:
            response = requests.head(url, timeout=5)  # Adjust timeout as needed
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            resources[resource_id_found]["url"] = url
        except RequestException as e:
            click.echo(Fore.RED + f"Error: Invalid URL '{url}': {e}" + Style.RESET_ALL)
            return
    if description:
        resources[resource_id_found]["description"] = description
    if category:
        resources[resource_id_found]["category"] = category

    save_resources(resources, dbpath)
    click.echo(
        Fore.GREEN + f"Resource '{name}' updated successfully." + Style.RESET_ALL
    )


@cli.command(hidden=True)
@click.argument("name")
@click.pass_context
def delete_resource(ctx, name):
    """Deletes a resource from the database."""
    resources = ctx.obj["resources"]
    dbpath = ctx.obj["dbpath"]
    resource_id = name.lower().replace(" ", "_")

    # Make the resource ID lookup case-insensitive
    resource_id_found = None
    for res_id in resources:
        if res_id.lower() == resource_id:
            resource_id_found = res_id
            break

    if resource_id_found is None:
        closest_match = find_closest_match(name, resources)
        error_message = f"Error: Resource '{name}' not found."
        if closest_match:
            error_message += f" Did you mean '{closest_match}'?"
        click.echo(Fore.RED + error_message + Style.RESET_ALL)
        return

    del resources[resource_id_found]
    save_resources(resources, dbpath)
    click.echo(
        Fore.GREEN + f"Resource '{name}' deleted successfully." + Style.RESET_ALL
    )


if __name__ == "__main__":
    cli()
