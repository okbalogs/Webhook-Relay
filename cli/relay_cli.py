import sys
import json
import time
import httpx
import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

app = typer.Typer(help="Webhook Relay & Replay CLI Local Tunnel Client")
console = Console()

@app.command()
def listen(
    target_url: str = typer.Option("http://localhost:3000/api/webhook", "--target", "-t", help="Local destination URL to forward webhooks to"),
    server_url: str = typer.Option("http://localhost:8000", "--server", "-s", help="Webhook Relay Platform Server URL"),
    endpoint_id: str = typer.Option(..., "--endpoint", "-e", help="Endpoint ID to listen on")
):
    """
    Subscribes to Webhook Relay SSE stream and forwards webhooks to local destination URL.
    """
    console.print(Panel.fit(
        f"[bold green]Webhook Relay Tunnel Client Active[/bold green]\n"
        f"[cyan]Server:[/cyan] {server_url}\n"
        f"[cyan]Endpoint ID:[/cyan] {endpoint_id}\n"
        f"[cyan]Local Destination Target:[/cyan] {target_url}",
        title="[bold blue]Relay CLI[/bold blue]"
    ))

    stream_url = f"{server_url}/api/v1/events/stream/live"
    
    with httpx.Client(timeout=None) as client:
        try:
            with client.stream("GET", stream_url) as response:
                console.print("[dim]Connected to SSE stream. Waiting for webhooks...[/dim]\n")
                
                buffer = ""
                for line in response.iter_lines():
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        try:
                            data = json.loads(data_str)
                            if data.get("endpoint_id") == endpoint_id:
                                event_id = data.get("event_id")
                                provider = data.get("provider", "generic")
                                event_type = data.get("event_type", "event")

                                console.print(f"[bold yellow]⚡ Inbound Webhook Received:[/bold yellow] [{provider}] {event_type} ({event_id})")
                                
                                # Forward request to local target
                                start = time.time()
                                try:
                                    fwd_res = httpx.post(target_url, json=data, timeout=10.0)
                                    duration = int((time.time() - start) * 1000)
                                    status_code = fwd_res.status_code
                                    if 200 <= status_code < 300:
                                        console.print(f"  [bold green]✓ Forwarded successfully to {target_url} -> HTTP {status_code} ({duration}ms)[/bold green]\n")
                                    else:
                                        console.print(f"  [bold red]✗ Forward failed -> HTTP {status_code} ({duration}ms)[/bold red]\n")
                                except Exception as fwd_err:
                                    console.print(f"  [bold red]✗ Local target error: {fwd_err}[/bold red]\n")
                        except Exception:
                            pass
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Stopping Relay CLI Tunnel.[/bold yellow]")
            sys.exit(0)
        except Exception as e:
            console.print(f"[bold red]Connection error: {e}[/bold red]")
            sys.exit(1)

if __name__ == "__main__":
    app()

