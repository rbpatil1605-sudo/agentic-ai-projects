def test_config_exports_expected_settings():
    from sales_agent.config import BQ_DATASET, BQ_SALES_TABLE, GCP_PROJECT_ID

    assert isinstance(GCP_PROJECT_ID, str)
    assert isinstance(BQ_DATASET, str)
    assert isinstance(BQ_SALES_TABLE, str)
