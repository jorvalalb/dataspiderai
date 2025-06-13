"""
catalogs.py – Central catalogues used by the CLI for contextual help
screens and downstream validation.
===================================================================

Includes:
  • METRICS_DOCS     – maps each snapshot header to its description
  • INSIDERS_COLS    – columns of the insiders table
  • MANAGERS_COLS    – columns of the Managers table
  • FUNDS_COLS       – columns of the Funds / ETFs table
  • RATINGS_COLS     – columns of the ratings table
  • NEWS_COLS        – columns of the news table
  • INCOME_COLS      – columns of the Income Statement YoY
  • BALANCE_COLS     – columns of the Balance Sheet YoY
  • CASH_COLS        – columns of the Cash Flow YoY
  • EXCHANGE_FILTERS – slug → filter code for "exch_xxx"
  • INDEX_FILTERS    – slug → filter code for "idx_xxx"
  • SECTOR_FILTERS   – slug → filter code for "sec_xxx"
  • INDUSTRY_CODES   – slug → industry code "ind_xxx"
  • COUNTRY_CODES    – slug → country code "geo_xxx"
  • INDUSTRY_SLUGS, COUNTRY_SLUGS, EXCH_SLUGS, IDX_SLUGS, SECTOR_SLUGS
    – lists for argparse.choices
  • make_industry_code, make_country_code – helpers for validation
"""

# ───────────────────────── Finviz snapshot metrics ──────────────────────────
METRICS_DOCS: dict[str, str] = {

    # ───── classic actions / ratios ─────
    "Index":                "Index membership (e.g. S&P 500)",
    "P/E":                  "Price-to-Earnings (ttm)",
    "EPS (ttm)":            "Earnings per Share (trailing 12 m)",
    "Insider Own":          "Shares owned by insiders (%)",
    "Shs Outstand":         "Shares outstanding",
    "Perf Week":            "Performance last week (%)",
    "Market Cap":           "Market capitalisation",
    "Forward P/E":          "Forward Price-to-Earnings",
    "EPS next Y":           "Projected EPS next fiscal year",
    "Insider Trans":        "Net insider transactions (6 m)",
    "Shs Float":            "Public-float shares",
    "Perf Month":           "Performance last month (%)",
    "Income":               "Net income (ttm)",
    "PEG":                  "P/E-to-Growth ratio",
    "EPS next Q":           "Projected EPS next quarter",
    "Inst Own":             "Institutional ownership (%)",
    "Short Float":          "Short interest as % of float",
    "Perf Quarter":         "Performance last quarter (%)",
    "Sales":                "Revenue (ttm)",
    "P/S":                  "Price-to-Sales ratio",
    "EPS this Y":           "EPS growth this fiscal year (%)",
    "Inst Trans":           "Institutional transactions (3 m)",
    "Short Ratio":          "Short-interest ratio",
    "Perf Half Y":          "Performance last 6 m (%)",
    "Book/sh":              "Book value per share",
    "P/B":                  "Price-to-Book ratio",
    "EPS next 5Y":          "Projected EPS growth (5 y CAGR)",
    "ROA":                  "Return on assets (%)",
    "Short Interest":       "Total shares short",
    "Perf Year":            "Performance last 12 m (%)",
    "Cash/sh":              "Cash per share",
    "P/C":                  "Price-to-Cash ratio",
    "ROE":                  "Return on equity (%)",
    "52W Range":            "52-week price range",
    "Perf YTD":             "Year-to-date performance (%)",
    "Dividend":             "Dividend yield (ttm)",
    "P/FCF":                "Price-to-Free-Cash-Flow",
    "EPS past 5Y":          "EPS growth past 5 y (%)",
    "ROI":                  "Return on investment (%)",
    "52W High":             "52-week high",
    "52W Low":              "52-week low",
    "Beta":                 "Beta coefficient",
    "Dividend Ex-Date":     "Last ex-dividend date",
    "Quick Ratio":          "Quick ratio",
    "Current Ratio":        "Current ratio",
    "EPS Y/Y":              "EPS year-over-year change (%)",
    "Oper. Margin":         "Operating margin (ttm) (%)",
    "RSI (14)":             "14-day RSI",
    "Volatility":           "30-day / 5-day volatility",
    "Employees":            "Number of employees",
    "Debt/Eq":              "Debt-to-Equity ratio",
    "LT Debt/Eq":           "Long-term Debt-to-Equity",
    "Sales Y/Y":            "Revenue year-over-year change (%)",
    "Profit Margin":        "Net profit margin (ttm) (%)",
    "Recom":                "Analyst recommendation (1–5)",
    "Target Price":         "Analyst consensus target price",
    "Option/Short":         "Options volume vs short interest",
    "EPS Q/Q":              "EPS quarter-over-quarter change (%)",
    "Payout":               "Dividend payout ratio (%)",
    "Rel Volume":           "Relative trading volume",
    "Prev Close":           "Previous close price",
    "Sales Surprise":       "Last-quarter sales surprise (%)",
    "EPS Surprise":         "Last-quarter EPS surprise (%)",
    "Sales Q/Q":            "Revenue quarter-over-quarter change (%)",
    "Avg Volume":           "Average daily volume (3 m)",
    "Price":                "Last trade price",
    "SMA20":                "20-day simple moving average (%)",
    "SMA50":                "50-day simple moving average (%)",
    "SMA200":               "200-day simple moving average (%)",
    "Volume":               "Current session volume",
    "Change":               "Price change today (%)",

     # ───── ETF / fund specific headers ─────
    "Category":             "Single category of the ETF",
    "Asset Type":           "Broad asset class (e.g. Commodities & Metals)",
    "Sponsor":              "Fund manager / issuing bank",
    "ETF Type":             "Asset-class + geo exposure bucket",
    "Tags":                 "ETF thematic tags (Finviz tag links)",
    "ETF Family":           "Fund family designated by the sponsor",
    "Index Weighting":      "Weighting method of underlying index",
    "Index":                "Underlying index tracked",
    "Bond Type":            "Type of bonds held by the ETF",
    "Commodity Type":       "Commodity category held",
    "Active/Passive":       "Actively managed vs. passive index-linked",
    "Quant Type":           "Underlying quant model strategy",
    "Structure Type":       "Legal structure (ETF, ETN, AST…)",
    "Region":               "Targeted regional exposure",
    "Sector/Theme":         "Targeted sector or investment theme",
    "Growth/Value":         "Style tilt stated in prospectus",
    "Dev/Emerg":            "Developed-/Emerging-market exposure",
    "Currency":             "Currency denomination of underlying assets",
    "NAV%":                 "NAV premium/discount vs. last price",
    "NAV/sh":               "Net Asset Value per share",
    "AUM":                  "Assets Under Management",
    "Total Holdings":       "Number of holdings in the ETF",
    "Return% 1Y":           "1-year annualised return",
    "Return% 3Y":           "3-year annualised return",
    "Return% 5Y":           "5-year annualised return",
    "Return% 10Y":          "10-year annualised return",
    "Return% SI":           "Annualised return since inception",
    "Flows% 1M":            "1-month net fund flows as % of AUM",
    "Flows% 3M":            "3-month net fund flows",
    "Flows% 1Y":            "1-year net fund flows",
    "Flows% YTD":           "YTD net fund flows",
    "Flows% 5Y":            "5-year net fund flows",
    "Dividend TTM":         "Trailing-twelve-months dividend",
    "Dividend Type":        "Dividend-oriented strategy type",
    "Expense":              "Gross expense ratio",
    "Inverse/Leveraged":    "Inverse or leveraged ETF flag",
    "Option/Short":         "Optionable / shortable availability",
}

# ───────────────────── Table schema catalogues ──────────────────────
INSIDERS_COLS = [
    "Insider", "Relationship", "Date", "Transaction", "Cost",
    "#Shares", "Value ($)", "#Shares Total", "SEC Form 4",
]

MANAGERS_COLS = ["Manager", "%"]
FUNDS_COLS    = ["Fund / ETF", "%"]

RATINGS_COLS = [
    "date", "action", "analyst", "rating_change", "price_target_change",
]

NEWS_COLS = ["datetime", "headline", "source", "url"]

INCOME_COLS = [
    "Metric", "TTM", "FY 2024", "FY 2023", "FY 2022",
    "FY 2021", "FY 2020", "FY 2019", "FY 2018",
]

BALANCE_COLS = [
    "Metric", "FY 2024", "FY 2023", "FY 2022", "FY 2021",
    "FY 2020", "FY 2019", "FY 2018", "FY 2017",
]

CASH_COLS = [
    "Metric", "TTM", "FY 2024", "FY 2023", "FY 2022",
    "FY 2021", "FY 2020", "FY 2019", "FY 2018",
]

# ──────────────────── ETF holdings ──────────────────────────────
HOLDINGS_BD_COLS   = ["category", "percent", "extracted_at"]
HOLDINGS_TOP10_COLS = ["name", "percent", "sector", "extracted_at"]

# ─────────────────────── Screener filter maps ────────────────────────
EXCHANGE_FILTERS = {s: f"exch_{s}" for s in ("amex", "cboe", "nasd", "nyse")}

INDEX_FILTERS    = {"sp500": "idx_sp500", "nasdaq100": "idx_ndx",
                    "djia": "idx_dji",    "russell2000": "idx_rut"}

SECTOR_FILTERS   = {s: f"sec_{s}" for s in (
    "basicmaterials","communicationservices","consumercyclical",
    "consumerdefensive","energy","financial","healthcare",
    "industrials","realestate","technology","utilities",
)}

# ──────────────────────── Industry codes ──────────────────────────
INDUSTRY_CODES = {
    slug: f"ind_{slug}" for slug in [
        "stocksonly", "exchangetradedfund", "advertisingagencies",
        "aerospacedefense", "agriculturalinputs", "airlines",
        "airportsairservices", "aluminum", "apparelmanufacturing",
        "apparelretail", "assetmanagement", "automanufacturers",
        "autoparts", "autotruckdealerships", "banksdiversified",
        "banksregional", "beveragesbrewers", "beveragesnonalcoholic",
        "beverageswineriesdistilleries", "biotechnology", "broadcasting",
        "buildingmaterials", "buildingproductsequipment",
        "businessequipmentsupplies", "capitalmarkets", "chemicals",
        "closedendfunddebt", "closedendfundequity", "closedendfundforeign",
        "cokingcoal", "communicationequipment", "computerhardware",
        "confectioners", "conglomerates", "consultingservices",
        "consumerelectronics", "copper", "creditservices",
        "departmentstores", "diagnosticsresearch", "discountstores",
        "drugmanufacturersgeneral", "drugmanufacturersspecialtygeneric",
        "educationtrainingservices", "electricalequipmentparts",
        "electroniccomponents", "electronicgamingmultimedia",
        "electronicscomputerdistribution", "engineeringconstruction",
        "entertainment", "farmheavyconstructionmachinery", "farmproducts",
        "financialconglomerates", "financialdatastockexchanges",
        "fooddistribution", "footwearaccessories",
        "furnishingsfixturesappliances", "gambling", "gold",
        "grocerystores", "healthcareplans", "healthinformationservices",
        "homeimprovementretail", "householdpersonalproducts",
        "industrialdistribution", "informationtechnologyservices",
        "infrastructureoperations", "insurancebrokers",
        "insurancediversified", "insurancelife",
        "insurancepropertycasualty", "insurancereinsurance",
        "insurancespecialty", "integratedfreightlogistics",
        "internetcontentinformation", "internetretail", "leisure",
        "lodging", "lumberwoodproduction", "luxurygoods", "marineshipping",
        "medicalcarefacilities", "medicaldevices", "medicaldistribution",
        "medicalinstrumentssupplies", "metalfabrication", "mortgagefinance",
        "oilgasdrilling", "oilgasep", "oilgasequipmentservices",
        "oilgasintegrated", "oilgasmidstream", "oilgasrefiningmarketing",
        "otherindustrialmetalsmining", "otherpreciousmetalsmining",
        "packagedfoods", "packagingcontainers", "paperpaperproducts",
        "personalservices", "pharmaceuticalretailers",
        "pollutiontreatmentcontrols", "publishing", "railroads",
        "realestatedevelopment", "realestatediversified",
        "realestateservices", "recreationalvehicles", "reitdiversified",
        "reithealthcarefacilities", "reithotelmotel", "reitindustrial",
        "reitmortgage", "reitoffice", "reitmortgage", "reitresidential",
        "reitretail", "reitspecialty", "rentalleasingservices",
        "residentialconstruction", "resortscasinos", "restaurants",
        "scientifictechnicalinstruments", "securityprotectionservices",
        "semiconductorequipmentmaterials", "semiconductors", "shellcompanies",
        "silver", "softwareapplication", "softwareinfrastructure", "solar",
        "specialtybusinessservices", "specialtychemicals",
        "specialtyindustrialmachinery", "specialtyretail",
        "staffingemploymentservices", "steel", "telecomservices",
        "textilemanufacturing", "thermalcoal", "tobacco", "toolsaccessories",
        "travelservices", "trucking", "uranium", "utilitiesdiversified",
        "utilitiesindependentpowerproducers", "utilitiesregulatedelectric",
        "utilitiesregulatedgas", "utilitiesregulatedwater",
        "utilitiesrenewable", "wastemanagement",
    ]
}
INDUSTRY_SLUGS = list(INDUSTRY_CODES.keys())


# ──────────────────────── Country codes ──────────────────────────
COUNTRY_CODES = {
    slug: f"geo_{slug}" for slug in [
        "usa", "notusa", "asia", "europe", "latinamerica", "bric",
        "argentina", "australia", "bahamas", "belgium", "benelux", "bermuda",
        "brazil", "canada", "caymanislands", "chile", "china",
        "chinahongkong", "colombia", "cyprus", "denmark", "finland",
        "france", "germany", "greece", "hongkong", "hungary", "iceland",
        "india", "indonesia", "ireland", "israel", "italy", "japan", "jordan",
        "kazakhstan", "luxembourg", "malaysia", "malta", "mexico", "monaco",
        "netherlands", "newzealand", "norway", "panama", "peru",
        "philippines", "portugal", "russia", "singapore", "southafrica",
        "southkorea", "spain", "sweden", "switzerland", "taiwan", "thailand",
        "turkey", "unitedarabemirates", "unitedkingdom", "uruguay", "vietnam",
    ]
}
COUNTRY_SLUGS = list(COUNTRY_CODES.keys())

# ──────────────────────── IPO date filters ──────────────────────────
IPO_FILTERS   = {v: f"ipodate_{v}" for v in (
    "today","yesterday","prevweek","prevmonth","prevquarter","prevyear",
    "prev2yrs","prev3yrs","prev5yrs",
    "more1","more5","more10","more15","more20","more25",
)}
CAP_FILTERS   = {v: f"cap_{v}" for v in (
    "mega","large","mid","small","micro","nano",
    "largeover","midover","smallover","microover",
    "largeunder","midunder","smallunder","microunder",
)}
PE_FILTERS    = {v: f"fa_pe_{v}"  for v in
                 ["low","profitable","high"] +
                 [f"u{x}" for x in (5,10,15,20,25,30,35,40,45,50)] +
                 [f"o{x}" for x in (5,10,15,20,25,30,35,40,45,50)]}
FPE_FILTERS   = {v: f"fa_fpe_{v}" for v in PE_FILTERS}     
PEG_FILTERS   = {v: f"fa_peg_{v}" for v in
                 ("low","high","u1","u2","u3","o1","o2","o3")}
PCASH_FILTERS = {v: f"fa_pc_{v}"  for v in
                 ["low","high"] +
                 [f"u{x}" for x in range(1,11)] +
                 [f"o{x}" for x in (1,2,3,4,5,6,7,8,9,10,20,30,40,50)]}
PS_FILTERS    = {v: f"fa_ps_{v}"  for v in
                 ["low","high"] +
                 [f"u{x}" for x in range(1,11)] +
                 [f"o{x}" for x in range(1,11)]}
PB_FILTERS    = {v: f"fa_pb_{v}"  for v in PS_FILTERS}     
AVG_VOL_FILTERS = {
    **{f"u{n}": f"sh_avgvol_u{n}" for n in ("50","100","500","750","1000")},
    **{f"o{n}": f"sh_avgvol_o{n}" for n in ("50","100","200","300","400",
                                            "500","750","1000","2000")},
    "100to500":   "sh_avgvol_100to500",
    "100to1000":  "sh_avgvol_100to1000",
    "500to1000":  "sh_avgvol_500to1000",
    "500to10000": "sh_avgvol_500to10000",
}

# ─── Tag filter ────────────────────────────────
_TAG_SLUGS = [
    # A–G
    "13f","3dprinting","5g","ai","aapl","aerospacedefense","africa","aggressive",
    "agriculture","aircraft","airlines","alcoholtobacco","amd","amzn","argentina",
    "arkk","asia","asiaexjapan","asiapacific","asiapacificexjapan","assetrotation",
    "aud","australia","austria","autoindustry","automation","autonomousvehicles",
    "baba","banks","batteries","bdc","belgium","betting","bigdata","biotechnology",
    "bitcoin","blockchain","bluechip","bonds","brazil","brokerage","buffer",
    "buyback",
    # C–F
    "cad","canada","cancer","cannabis","capitalmarkets","carbonallowances",
    "carbonlow","cashcow","casino","catholicvalues","chf","chile","china",
    "cleanenergy","climatechange","clinicaltrials","clo","cloudcomputing","cobalt",
    "coin","colombia","commodity","communicationservices","communitybanks",
    "conservative","consumer","consumerdiscretionary","consumerstaples",
    "convertiblesecurities","copper","corn","corporatebonds","coveredcall","crypto",
    "cryptospot","currencies","currency","currencybonds","customer","cybersecurity",
    "datacenters","dax","debt","debtsecurities","democrats","denmark","derivatives",
    "developed","developedexjapan","developedexus","digitalinfrastructure",
    "digitalpayments","dis","disasterrecovery","disruptive","dividend",
    "dividendgrowth","dividendweight","djia","drybulk","ecommerce","esports",
    "eafe","education","egypt","electricvehicles","electricity","emerging",
    "emergingexchina","energy","energymanagement","energyproducers","energystorage",
    "entertainment","environmental","equalweight","equity","esg","etfs","ethereum",
    "eur","europe","eurozone","exenergy","exfinancial","exfossilfuels",
    "exhealthcare","extechnology","exchanges","factorrotation","fang","financial",
    "finland","fintech","fixedincome","fixedperiod","floatingrate","food",
    "foodbeverage","fossilfuels","france","fundamental","fundamentalweight",
    "futures",
    # G–M
    "gaming","gbp","gender","genomics","germany","gld","global","globalexus",
    "gold","goldminers","googl","governmentbonds","greece","growth","hardware",
    "healthcare","hedgecurrency","hedgefund","hedgeinflation","hedgerates",
    "hedgerisk","highbeta","highyield","homeconstruction","homeoffice","honkkong",
    "hotel","hydrogen","it","income","india","indonesia","industrials","inflation",
    "infrastructure","innovation","insurance","international","internet",
    "internetofthings","inverse","investmentgrade","ipo","ireland","israel",
    "italy","japan","jimcramer","jpm","jpy","kuwait","largecap","latinamerica",
    "leadership","leverage","lifestyle","lithium","loans","longshort","luxury",
    # M–S
    "ma","machinelearning","macro","malaysia","marketsentiment","marketing",
    "materials","mbs","media","medical","megacap","meta","metals","metaverse",
    "mexico","microcap","midcap","midlargecap","midstream","military","millennial",
    "miners","mlp","mobilepayments","moderate","momentum","monopolies","msft",
    "multiasset","multifactor","multisector","municipalbonds","music","nasdaqcomposite",
    "nasdaq100","naturalgas","naturalresources","netherlands","network",
    "newzealand","nextgen","nflx","nickel","nigeria","nikkei400","nonesg",
    "northamerica","norway","nuclearenergy","nvda","ocean","oil","oilgasexpprod",
    "oilgasservices","onlinestores","options","pakistan","palladium","patents",
    "peru","petcare","pharmaceutical","philippines","physical","pipelines",
    "platinum","poland","politics","portugal","preciousmetals","preferred",
    "preferredsecurities","privatecredit","privateequity","putwrite","pypl",
    "quality","quantitative","quantumcomputing","quatar","rd","rareearth",
    "realassets","realestate","regionalbanks","reits","relativestrength",
    "renewableenergy","republicans","responsible","restaurant","retail",
    "retailstores","revenue","risingrates","robotics","russell1000","russell200",
    "russell2000","russell2500","russell3000","saudiarabia","sectorrotation",
    "semiconductors","seniorloans","shariacompliant","shipping","short","silver",
    "silverminers","singapore","singleasset","slv","smallcap","smallmidcap",
    "smartgrid","smartmobility","social","socialmedia","software","solar",
    "southafrica","southkorea","soybean","sp100","sp1000","sp1500","sp400",
    "sp500","sp600","spac","spaceexploration","spain","spinoff","steel","sugar",
    "sukuk","sustainability","sweden","switzerland","tactical","taiwan",
    "targetdrawdown","technology","thailand","timber","tips","transportation",
    "travel","treasuries","tsla","turkey","uk","us","uae","upsidecap","upstream",
    "uranium","uraniumminers","usd","uso","utilities","value","variablerate","vegan",
    "vietnam","vix","volatility","volatilityindex","volatilityweight","water",
    "weapons","wellness","wheat","wind","wood","xom","yuan","zerocoupon"
]
TAG_FILTERS = {slug: f"etf_tags_{slug}" for slug in _TAG_SLUGS}

# ═════════════════════ argparse.choices ══════════════════════════
TAG_SLUGS       = _TAG_SLUGS
EXCH_SLUGS      = list(EXCHANGE_FILTERS)
IDX_SLUGS       = list(INDEX_FILTERS)
SECTOR_SLUGS    = list(SECTOR_FILTERS)
INDUSTRY_SLUGS  = list(INDUSTRY_CODES)
COUNTRY_SLUGS   = list(COUNTRY_CODES)
IPO_SLUGS       = list(IPO_FILTERS)
CAP_SLUGS       = list(CAP_FILTERS)
PE_SLUGS        = list(PE_FILTERS)
FPE_SLUGS       = list(FPE_FILTERS)
PEG_SLUGS       = list(PEG_FILTERS)
PCASH_SLUGS     = list(PCASH_FILTERS)
PS_SLUGS        = list(PS_FILTERS)
PB_SLUGS        = list(PB_FILTERS)
AVG_VOL_SLUGS   = list(AVG_VOL_FILTERS)

# ═════════════════════ Helpers ═══════════════════════════════════════════════
def make_industry_code(slug: str) -> str | None:
    return INDUSTRY_CODES.get(slug.lower())
def make_country_code(slug: str) -> str | None:
    return COUNTRY_CODES.get(slug.lower())

# ═════════════════════ __all__ export  ═══════════════════════════════════════
__all__ = [
    "METRICS_DOCS","INSIDERS_COLS","MANAGERS_COLS","FUNDS_COLS","RATINGS_COLS",
    "NEWS_COLS","INCOME_COLS","BALANCE_COLS","CASH_COLS",
    "EXCHANGE_FILTERS","INDEX_FILTERS","SECTOR_FILTERS",
    "INDUSTRY_CODES","COUNTRY_CODES","IPO_FILTERS","CAP_FILTERS","PE_FILTERS",
    "FPE_FILTERS","PEG_FILTERS","PCASH_FILTERS","PS_FILTERS","PB_FILTERS",
    "AVG_VOL_FILTERS","TAG_FILTERS",
    "EXCH_SLUGS","IDX_SLUGS","SECTOR_SLUGS","INDUSTRY_SLUGS","COUNTRY_SLUGS",
    "IPO_SLUGS","CAP_SLUGS","PE_SLUGS","FPE_SLUGS","PEG_SLUGS","PCASH_SLUGS",
    "PS_SLUGS","PB_SLUGS","AVG_VOL_SLUGS","TAG_SLUGS",
    "make_industry_code","make_country_code",
]