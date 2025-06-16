import pandas as pd
from data_agent import _bs_statement_to_df

SAMPLE_HTML = """
<table data-testid="quote-statements-table">
  <tr><td>Metric</td><td>Skip</td><td>2023</td><td>2022</td></tr>
  <tr><td>Revenue</td><td>foo</td><td>100</td><td>90</td></tr>
  <tr><td>Profit</td><td>bar</td><td>10</td><td>5</td></tr>
</table>
"""

def test_bs_statement_to_df_basic():
    df = _bs_statement_to_df(SAMPLE_HTML)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["Metric", "extracted_at", "2023", "2022"]
    assert df.loc[0, "Metric"] == "Revenue"
    assert df.loc[1, "2022"] == "5"
