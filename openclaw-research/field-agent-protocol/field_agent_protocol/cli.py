"""
CLI interface for The Field Agent Protocol
"""

import sys
import argparse
from pathlib import Path

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="The Field Agent Protocol (TFAP)")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize field network')
    init_parser.add_argument('--force', action='store_true', help='Force overwrite existing files')
    
    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover available agents')
    discover_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup new field agent')
    setup_parser.add_argument('--id', help='Agent ID')
    setup_parser.add_argument('--name', help='Agent name')
    setup_parser.add_argument('--capabilities', help='Comma-separated capabilities')
    
    # Identity command
    identity_parser = subparsers.add_parser('identity', help='Show agent identity')
    identity_parser.add_argument('--verbose', action='store_true', help='Show detailed identity info')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        from .initialize import initialize_field_network
        initialize_field_network(args.force)
    elif args.command == 'discover':
        from .discovery import discover_agents
        agents = discover_agents()
        if args.json:
            import json
            print(json.dumps(agents, indent=2))
        else:
            print_agents_list(agents)
    elif args.command == 'setup':
        from .setup_agent import setup_field_agent
        setup_field_agent(args.id, args.name, args.capabilities)
    elif args.command == 'identity':
        from .setup_agent import load_agent_config
        config = load_agent_config()
        if config:
            if args.verbose:
                print_verbose_identity(config)
            else:
                print_identity(config)
        else:
            print("❌ No agent identity configured")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

def print_agents_list(agents):
    """Print list of discovered agents"""
    print("🌐 Available Field Agents:")
    for agent in agents:
        print(f"  • {agent['name']} ({agent['agent_id']})")
        print(f"    Capabilities: {', '.join(agent['capabilities'])}")
        print(f"    Trust: {agent['tippss']['trust']}")
        print(f"    Status: {agent['field_state']}")

def print_identity(config):
    """Print agent identity"""
    print(f"🤖 Agent Identity:")
    print(f"  Name: {config['name']}")
    print(f"  ID: {config['agent_id']}")
    print(f"  Capabilities: {', '.join(config['capabilities'])}")

def print_verbose_identity(config):
    """Print detailed agent identity"""
    print(f"🔍 Detailed Agent Identity:")
    print(f"  Name: {config['name']}")
    print(f"  ID: {config['agent_id']}")
    print(f"  Capabilities: {', '.join(config['capabilities'])}")
    print(f"  TIPPSS Scores:")
    for key, value in config['tippss_scores'].items():
        print(f"    - {key}: {value}")
    print(f"  Resources: {', '.join(config.get('resources', []))}")
    print(f"  Setup Time: {config.get('setup_timestamp', 'Unknown')}")

if __name__ == "__main__":
    main()
