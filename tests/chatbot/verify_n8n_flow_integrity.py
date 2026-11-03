import json

def verify_flow():
    with open('flows/n8n/V8_ChatbotReservas.json', 'r', encoding='utf-8') as f:
        flow = json.load(f)

    nodes = flow['nodes']
    connections = flow['connections']

    node_names = {n['name'] for n in nodes}
    print(f"Total nodes in flow: {len(nodes)}")

    # 1. Check all connection sources and targets exist
    broken_sources = []
    broken_targets = []
    connected_nodes = set()

    for source_node, conn_types in connections.items():
        if source_node not in node_names:
            broken_sources.append(source_node)
        connected_nodes.add(source_node)

        for conn_type, output_branches in conn_types.items():
            for branch_idx, targets in enumerate(output_branches):
                for target_info in targets:
                    target_node = target_info.get('node')
                    if target_node not in node_names:
                        broken_targets.append((source_node, target_node))
                    else:
                        connected_nodes.add(target_node)

    print(f"Broken connection sources: {broken_sources}")
    print(f"Broken connection targets: {broken_targets}")

    # 2. Check orphan nodes (nodes that have no incoming or outgoing connections, except Webhook which is entry point)
    orphans = []
    entry_nodes = {'WhatsApp Webhook', 'Webhook Verificación'}
    for n in nodes:
        name = n['name']
        if name not in connected_nodes and name not in entry_nodes:
            orphans.append(name)

    print(f"Orphan (unconnected) nodes: {orphans}")

    # 3. Check all switch nodes and their rule outputs
    switch_issues = []
    for n in nodes:
        if 'switch' in n.get('type', ''):
            name = n['name']
            rules = n.get('parameters', {}).get('rules', {}).get('values', [])
            has_fallback = n.get('parameters', {}).get('options', {}).get('fallbackOutput') == 'extra'
            expected_outputs = len(rules) + (1 if has_fallback else 0)

            node_conns = connections.get(name, {}).get('main', [])
            actual_outputs = len(node_conns)
            if actual_outputs != expected_outputs:
                switch_issues.append((name, f"Expected {expected_outputs} outputs, found {actual_outputs} in connections"))

    print(f"Switch node routing issues: {switch_issues}")

    if not broken_sources and not broken_targets and not orphans and not switch_issues:
        print("\n>>> ALL CHECKS PASSED: 100% INTEGRITY, ZERO BROKEN LINKS, ZERO ORPHANS, ZERO SWITCH MISMATCHES <<<")

if __name__ == '__main__':
    verify_flow()

