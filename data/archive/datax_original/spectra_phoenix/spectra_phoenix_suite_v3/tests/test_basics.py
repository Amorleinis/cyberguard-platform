def test_imports():
    import importlib
    mods = ['hetero_gnn_demo', 'tgn_template', 'rl_remediation_env']
    for m in mods:
        importlib.import_module(m)
    assert True
