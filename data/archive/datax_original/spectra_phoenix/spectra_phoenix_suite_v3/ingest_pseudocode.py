# ingest_pseudocode.py
# Pseudocode for updating a graph store from telemetry events.
# Replace HeteroGraphStore with your chosen DB (Neo4j, RedisGraph, DGraph, etc).

class HeteroGraphStore:
    def ensure_node(self, ntype, nid, attrs=None):
        pass
    def set_node(self, ntype, nid, attrs=None):
        pass
    def add_edge(self, etype, src_type, dst_type, src, dst, attrs=None):
        pass

graph_store = HeteroGraphStore()

def handle_event(evt):
    if evt['type']=='process_spawn':
        graph_store.ensure_node('host', evt['host_id'], attrs={'id':evt['host_id']})
        proc_node = f\"proc:{evt['host_id']}:{evt['pid']}\"
        graph_store.set_node('process', proc_node, attrs={'pid':evt['pid'],'cmdline':evt['cmdline']})
        graph_store.add_edge('runs', 'host', 'process', src=evt['host_id'], dst=proc_node, attrs={'ts':evt['ts']})
    elif evt['type']=='network_conn':
        ep = f\"ep:{evt['dst_ip']}\"
        graph_store.set_node('endpoint', ep, attrs={'ip':evt['dst_ip']})
        graph_store.add_edge('connects', 'process', 'endpoint', src=evt['proc_node'], dst=ep, attrs={'port':evt['dst_port'],'bytes':evt['bytes'],'ts':evt['ts']})
    # ... handle other event types

# periodically snapshot subgraphs around recent alerts and send to model server as batched inference jobs
