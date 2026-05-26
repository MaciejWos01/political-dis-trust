# Use a refined search strings for detecting tweets relating to the US government
import json
import time
import re
import regex

try:
    import orjson as _orjson

    def _dumps_obj(obj):
        return _orjson.dumps(obj).decode('utf-8')
except ImportError:
    def _dumps_obj(obj):
        return json.dumps(obj, ensure_ascii=False)

OUTFILE_BUFFER_BYTES = 1 << 20

# Specify the input and output file names
# input_file = 'Merged Coding Sets 1 and 2 Raw.jsonl'
# output_file = 'Merged Coding Sets 1 and 2 with New Matched Terms.jsonl'
input_file = 'web-immunization_participants_tweets.jsonl'
output_file = 'Political Institutions Tweets using GPT Codex New Handles.jsonl'
# input_file = 'Test_Tweets.jsonl'
# output_file = 'Test Tweets Results.jsonl'

# Log progress every N documents (set to 1 to log every line)
PROGRESS_EVERY = 10_000

# Define a list of search terms or patterns
US_institutions = [r"AbilityOne Commission", r"Access Board", r"Administration for Children and Families", 
                   r"Administration for Community Living", r"Administration for Native Americans", 
                   r"Administrative Conference of the United States", r"Administrative Office of the U\.S\. Courts", r"Administrative Office of the US Courts",
                   r"Administrator", r"Advisory Council on Historic Preservation", r"Africa Command", 
                   r"African Development Foundation", r"Agency for Global Media", 
                   r"Agency for Healthcare Research and Quality", r"Agency for International Development", 
                   r"Agency for Toxic Substances and Disease Registry", r"Agricultural Marketing Service", 
                   r"Agricultural Research Service", r"Agriculture Department", r"Agriculture Library", 
                   r"US Air Force", r"Air Force Reserve", 
                   r"Air Force Reserve Command", r"Alcohol and Tobacco Tax and Trade Bureau", 
                   r"Alcohol\, Tobacco\, Firearms and Explosives Bureau", r"Alhurra TV", 
                   r"American Battle Monuments Commission", r"AmeriCorps", r"AmeriCorps Seniors", 
                   r"Animal and Plant Health Inspection Service", r"Antitrust Division", 
                   r"Appalachian Regional Commission", r"Archives\, National Archives and Records Administration", 
                   r"Arctic Research Commission", r"Armed Forces Retirement Home", 
                   r"Arms Control and International Security", r"Army Corps of Engineers", 
                   r"Assistant Secretary for Research and Technology", r"Attorney General", r"Assistant Attorney General",
                   r"Bankruptcy Courts", 
                   r"Barry M\. Goldwater Scholarship and Excellence in Education Foundation", 
                   r"Bonneville Power Administration", r"Bureau of Alcohol and Tobacco Tax and Trade", 
                   r"Bureau of Alcohol\, Tobacco\, Firearms and Explosives", r"Bureau of Consular Affairs", 
                   r"Bureau of Consumer Financial Protection", r"Bureau of Economic Analysis", 
                   r"Bureau of Engraving and Printing", r"Bureau of Indian Affairs", r"Bureau of Industry and Security", 
                   r"Bureau of International Labor Affairs", r"Bureau of Justice Statistics", r"Bureau of Labor Statistics", 
                   r"Bureau of Land Management", r"Bureau of Ocean Energy Management", r"Bureau of Prisons", 
                   r"Bureau of Reclamation", r"Bureau of Safety and Environmental Enforcement", r"Bureau of the Census", 
                   r"Bureau of the Fiscal Service", r"Bureau of Transportation Statistics", r"Bureau ofTransportation Statistics", 
                   r"Cabinet", r"Capitol Police", r"Capitol Visitor Center", r"Census Bureau", 
                   r"Center for Nutrition Policy and Promotion", r"Center for Parent Information and Resources", 
                   r"Centers for Disease Control and Prevention", r"Centers for Medicare and Medicaid Services", 
                   r"Central Command", r"Central Intelligence Agency", r"Chemical Safety Board", 
                   r"Chief Acquisition Officers Council", r"Chief Financial Officers Council", 
                   r"Chief Human Capital Officers Council", r"Chief Information Officers Council", r"Chief Justice", 
                   r"Circuit Courts of Appeal", r"Citizens' Stamp Advisory Committee", r"Citizenship and Immigration Services", 
                   r"Civil Rights Division\, Department of Justice", r"Coast Guard", r"Commerce Department", 
                   r"Commission of Fine Arts", r"Commission on Civil Rights", r"Commission on International Religious Freedom", 
                   r"Commission on Presidential Scholars", r"Commission on Security and Cooperation in Europe", 
                   r"Committee on Foreign Investment in the United States", r"Commodity Futures Trading Commission", 
                   r"Community Oriented Policing Services", r"Community Planning and Development", r"Comptroller of the Currency", r"(?:Republicans|Reps) in Congress", r"(?:Democrats|Dems) in Congress",
                   r"(?<![A-Za-z0-9])(?!(?:Republicans|Reps|Democrats|Dems)\s+in\s+)(?!Members of )Congress(?![A-Za-z0-9])(?!\s+(Members|people))", r"Congressional Budget Office", r"Congressional Research Service", r"Congressmen", 
                   r"Congresswomen", r"Congressmembers", r"Congress Members", r"Members of Congress", r"Congress people", r"Consumer Financial Protection Bureau", 
                   r"Consumer Product Safety Commission", r"Coordinating Council on Juvenile Justice and Delinquency Prevention", 
                   r"Copyright Office", r"Corps of Engineers", r"Council of Economic Advisers", 
                   r"Council of the Inspectors General on Integrity and Efficiency", r"Council on Environmental Quality", 
                   r"Court of Appeal", r"Court of Appeals for the Armed Forces", r"Court of Appeals for the Federal Circuit", 
                   r"Court of Appeals for Veterans Claims", r"Court of Federal Claims", r"Court of International Trade", 
                   r"Court Services and Offender Supervision Agency for the District of Columbia", r"Courts of Appeal", 
                   r"Customs and Border Protection", r"Cyber Command", r"Cybersecurity and Infrastructure Security Agency", 
                   r"Debt and Claims Management Center", r"Defense Advanced Research Projects Agency", r"Defense Commissary Agency", 
                   r"Defense Contract Audit Agency", r"Defense Contract Management Agency", 
                   r"Defense Counterintelligence and Security Agency", r"Defense Department", r"Defense Finance and Accounting Service", 
                   r"Defense Finance and Accounting Service Debt and Claims Management Center", r"Defense Health Agency", 
                   r"Defense Information Systems Agency", r"Defense Intelligence Agency", r"Defense Logistics Agency", 
                   r"Defense Nuclear Facilities Safety Board", r"Defense POW\/MIA Accounting Agency", 
                   r"Defense Security Cooperation Agency", r"Defense Technical Information Center", 
                   r"Defense Threat Reduction Agency", r"Delaware River Basin Commission", r"Delta Regional Authority", 
                   r"Denali Commission", r"Department of Agriculture", r"Department of Commerce", r"Department of Defense", 
                   r"Department of Education", r"Department of Energy", r"Department of Energy’s Office of Science", 
                   r"Department of Health and Human Services", r"Department of Homeland Security", r"Department of Housing and Urban Development", 
                   r"Department of Interior", r"Department of Justice", r"Department of Labor", r"Department of State", 
                   r"Department of the Interior", r"Department of the Treasury", r"Department of Transportation", 
                   r"Department of Treasury", r"Department of Veterans Affairs", r"Director of National Intelligence", 
                   r"Drug Enforcement Administration", r"Economic Development Administration", 
                   r"Economic Growth\, Energy\, and the Environment", r"Economic Research Service", r"Education Department", 
                   r"Elder Justice Initiative", r"Election Assistance Commission", r"Employee Benefits Security Administration", 
                   r"Employment and Training Administration", r"Energy Department", 
                   r"Energy Information Administration", r"Environmental Protection Agency", 
                   r"Equal Employment Opportunity Commission", r"European Command", r"Executive Office for Immigration Review", 
                   r"Export-Import Bank of the United States", r"Fair Housing and Equal Opportunity", r"Fannie Mae", 
                   r"Farm Credit Administration", r"Farm Credit System Insurance Corporation", r"Farm Service Agency", 
                   r"Federal Accounting Standards Advisory Board", r"Federal Aviation Administration", 
                   r"Federal Bureau of Investigation", r"Federal Bureau of Prisons", r"Federal Committee on Statistical Methodology", 
                   r"Federal Communications Commission", r"Federal Deposit Insurance Corporation", r"Federal Election Commission", 
                   r"Federal Emergency Management Agency", r"Federal Energy Regulatory Commission", 
                   r"Federal Financial Institutions Examination Council", r"Federal Financing Bank", 
                   r"Federal Geographic Data Committee", r"Federal Highway Administration", r"Federal Housing Administration", 
                   r"Federal Housing Finance Agency", r"Federal Judicial Center", r"Federal Labor Relations Authority", 
                   r"Federal Laboratory Consortium for Technology Transfer", r"Federal Law Enforcement Training Centers", 
                   r"Federal Library and Information Network", r"Federal Maritime Commission", 
                   r"Federal Mediation and Conciliation Service", r"Federal Mine Safety and Health Review Commission", 
                   r"Federal Motor Carrier Safety Administration", r"Federal Protective Service", r"Federal Railroad Administration", 
                   r"Federal Register", r"Federal Reserve System", r"Federal Retirement Thrift Investment Board", 
                   r"Federal Student Aid Information Center", r"Federal Trade Commission", r"Federal Transit Administration", 
                   r"Federal Voting Assistance Program", r"FedStats", r"Fire Administration", 
                   r"Fish and Wildlife Service", r"Fleet Forces Command", r"Food and Drug Administration", 
                   r"Food and Nutrition Service", r"Food Safety and Inspection Service", r"Foreign Agricultural Service", 
                   r"Foreign Claims Settlement Commission", r"Forest Service", r"Freddie Mac", 
                   r"General Services Administration", r"Geological Survey", r"Ginnie Mae", r"Government(?![A-Za-z0-9])(?!\s?officials)", r"Government officials", r"(?<![A-Za-z0-9])Governors(?![A-Za-z0-9])",
                   r"Government Accountability Office", r"Government Publishing Office", r"Harry S\. Truman Scholarship Foundation", 
                   r"Head of department", r"Head of the department", r"Health and Human Services Department", 
                   r"Health Resources and Services Administration", r"Helsinki Commission", r"Holocaust Memorial Museum", 
                   r"Homeland Security Department", r"Hour and Wage Division", r"House of Representatives", 
                   r"House Office of Inspector General", r"House Office of the Clerk", r"HouseDemocrats", r"House Democrats", r"HouseRepublicans", r"House Republicans", r"HouseGOP", 
                   r"Housing Office", r"Human Foods Program", r"Immigrant and Employee Rights Section", 
                   r"Immigration and Citizenship Services", r"Immigration and Customs Enforcement", r"Indian Arts and Crafts Board", 
                   r"Indian Health Service", r"Indo-Pacific Command", r"Inspectors General", r"Institute of Education Sciences", 
                   r"Institute of Museum and Library Services", r"Interagency Alternative Dispute Resolution Working Group", 
                   r"Interagency Committee for the Management of Noxious and Exotic Weeds", r"Inter-American Foundation", 
                   r"Interior Department", r"Internal Revenue Service", r"International Development Finance Corporation", 
                   r"International Trade Administration", r"International Trade Commission", r"Interpol", 
                   r"James Madison Memorial Fellowship Foundation", r"Japan-United States Friendship Commission", r"Job Corps", 
                   r"John F\. Kennedy Center for the Performing Arts", r"Joint Board for the Enrollment of Actuaries", 
                   r"Joint Chiefs of Staff", r"Joint Fire Science Program", 
                   r"Joint Forces Staff College", 
                   r"Joint Program Executive Office for Chemical\, Biological\, Radiological and Nuclear Defense", 
                   r"Judicial Circuit Courts of Appeal", r"Judicial Panel on Multidistrict Litigation", r"Judiciary Commitee", 
                   r"Justice Department", r"Justices of the Supreme Court", r"Supreme Justices", r"Kennedy Center", r"Labor Department", 
                   r"Legal Services Corporation", r"Library of Congress", r"Marine Corps", r"Marine Mammal Commission", 
                   r"Maritime Administration", r"Marshals Service", r"Mediation and Conciliation Service", r"Medicaid", 
                   r"Medicaid and CHIP Payment and Access Commission", r"Medicare", r"Medicare Payment Advisory Commission", 
                   r"Merit Systems Protection Board", r"Middle East Broadcasting Networks", r"Migratory Bird Conservation Commission", 
                   r"Military Academy\, West Point", r"Military Postal Service Agency", r"Millennium Challenge Corporation", 
                   r"Mine Safety and Health Administration", r"Minority Business Development Agency", r"Missile Defense Agency", 
                   r"Mission to the United Nations", r"Mississippi River Commission", r"National Aeronautics and Space Administration", 
                   r"National Agricultural Library", r"National Agricultural Statistics Service", r"National Archives and Records Administration", 
                   r"National Cancer Institute", r"National Capital Planning Commission", r"National Cemetery Administration", 
                   r"National Center for Complementary and Integrative Health", r"National Constitution Center", r"National Council on Disability", 
                   r"National Credit Union Administration", r"National Defense University", r"National Endowment for the Arts", 
                   r"National Endowment for the Humanities", r"National Flood Insurance Program", r"National Gallery of Art", 
                   r"National Geospatial-Intelligence Agency", r"National Guard", r"National Health Information Center", 
                   r"National Heart\, Lung\, and Blood Institute", r"National Highway Traffic Safety Administration", 
                   r"National Indian Gaming Commission", r"National Institute for Occupational Safety and Health", 
                   r"National Institute of Allergy and Infectious Diseases", r"National Institute of Arthritis\, Musculoskeletal and Skin Diseases", 
                   r"National Institute of Corrections", r"National Institute of Deafness and Other Communication Disorders", 
                   r"National Institute of Diabetes and Digestive and Kidney Diseases", r"National Institute of Food and Agriculture", 
                   r"National Institute of Justice", r"National Institute of Mental Health", 
                   r"National Institute of Neurological Disorders and Stroke", r"National Institute of Standards and Technology", 
                   r"National Institutes of Health", r"National Interagency Fire Center", r"National Invasive Species Information Center", 
                   r"National Labor Relations Board", r"National Laboratories", r"National Library of Medicine", r"National Marine Fisheries Service", 
                   r"National Mediation Board", r"National Nuclear Security Administration", r"National Ocean Service", 
                   r"National Oceanic and Atmospheric Administration", r"National Park Foundation", r"National Park Service", 
                   r"National Pesticide Information Center", r"National Prevention Information Network", 
                   r"National Reconnaissance Office", r"National Science Foundation", r"National Security Agency", 
                   r"National Security Council", r"National Technical Information Service", 
                   r"National Telecommunications and Information Administration", r"National Transportation Safety Board", 
                   r"National Weather Service", r"Natural Resources Conservation Service", r"Navy", r"NOAA Fisheries", 
                   r"Northern Border Regional Commission", r"Northern Command", r"Nuclear Regulatory Commission", 
                   r"Nuclear Waste Technical Review Board", r"Oak Ridge National Laboratory", 
                   r"Occupational Safety and Health Administration", r"Occupational Safety and Health Review Commission", 
                   r"Office for Civil Rights\, Department of Education", 
                   r"Office for Civil Rights\, Department of Health and Human Services", 
                   r"Office of Career\, Technical\, and Adult Education", r"Office of Child Support Enforcement", 
                   r"Office of Child Support Services", r"Office of Civil Rights\, Department of Education", 
                   r"Office of Community Planning and Development", r"Office of the Comptroller of the Currency", 
                   r"Office of Congressional Workplace Rights", r"Office of Cuba Broadcasting", 
                   r"Office of Disability Employment Policy", r"Office of Elementary and Secondary Education", 
                   r"Office of Energy Efficiency and Renewable Energy", r"Office of English Language Acquisition", 
                   r"Office of Environmental Management", r"Office of Fair Housing and Equal Opportunity", 
                   r"Office of Fossil Energy and Carbon Management", r"Office of Government Ethics", r"Office of Housing", 
                   r"Office of Immigrant and Employee Rights", r"Office of Investor Education and Advocacy", 
                   r"Office of Justice Programs", r"Office of Juvenile Justice and Delinquency Prevention", 
                   r"Office of Lead Hazard Control and Healthy Homes", r"Office of Local Defense Community Cooperation", 
                   r"Office of Management and Budget", r"Office of Manufactured Housing Programs", r"Office of Minority Health", 
                   r"Office of Multifamily Housing Programs", r"Office of National Drug Control Policy", 
                   r"Office of Natural Resources Revenue", r"Office of Nuclear Energy", r"Office of Pardon Attorney", 
                   r"Office of Personnel Management", r"Office of Policy Development and Research", 
                   r"Office of Postsecondary Education", r"Office of Refugee Resettlement", 
                   r"Office of Science and Technology Policy", r"Office of Scientific and Technical Information", 
                   r"Office of Servicemember Affairs", r"Office of Special Counsel", 
                   r"Office of Special Education and Rehabilitative Services", 
                   r"Office of Surface Mining\, Reclamation and Enforcement", r"Office of Textiles and Apparel", 
                   r"Office of the Federal Register", r"Office of the Pardon Attorney", r"Office of Weights and Measures", 
                   r"Office on Violence Against Women", r"Open World Leadership Center", r"Pacific Command", 
                   r"Parent Information and Resources Center", r"Parole Commission", r"Patent and Trademark Office", 
                   r"Peace Corps", r"Pension Benefit Guaranty Corporation", r"Pentagon Force Protection Agency", 
                   r"Pipeline and Hazardous Materials Safety Administration", r"Policy Development and Research", 
                   r"Postal Inspection Service", r"Postal Regulatory Commission", r"Postal Service", r"Postmaster General", r"(?<![A-Za-z0-9])President(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])President-elect(?![A-Za-z0-9])"
                   r"Presidential Scholars Commission", r"President's Council on Fitness\, Sports and Nutrition", r"Presidio Trust", 
                   r"Pretrial Services Agency for the District of Columbia", r"Prevention Information Network", 
                   r"Privacy and Civil Liberties Oversight Board", r"Public and Indian Housing", r"Radio and TV Martí", 
                   r"Radio Free Asia", r"Radio Free Europe and Radio Liberty", r"Radio Sawa", r"Railroad Retirement Board", 
                   r"Rehabilitation Services Administration", r"Risk Management Agency", r"Rural Business-Cooperative Service", 
                   r"Rural Development", r"Rural Housing Service", r"Rural Utilities Service", 
                   r"Saint Lawrence Seaway Development Corporation", r"Secret Service", 
                   r"Secretary of State", r"Secretary of the Treasury", r"Secretary of Defense", r"Secretary of the Interior", r"Secretary of Agriculture", r"Secretary of Commerce", r"Secretary of Labor", 
                   r"Secretary of Health and Human Services", r"Secretary of Housing and Urban Development", r"Secretary of Transportation", r"Secretary of Energy", r"Secretary of Education", 
                   r"Secretary of Veterans Affairs", r"Secretary of Homeland Security",                     
                   r"Securities and Exchange Commission", r"Selective Service System", 
                   r"(?<![A-Za-z0-9])(?<!(Republican|Rep|GOP|Democrat|Dem|Democratic)\s+)Senators(?![A-Za-z0-9])",
                   r"Senate Majority Leader", r"Senate Minority Leader", r"SenateRepublicans", r"SenateReps", r"Senate Republicans", r"Senate Reps", r"SenateDemocrats", r"SenateDems", r"Senate Democrats", r"Senate Dems", 
                   r"Republican Senator(?![A-Za-z0-9])", r"Rep Senator(?![A-Za-z0-9])", r"GOP Senator(?![A-Za-z0-9])", r"Democratic Senator(?![A-Za-z0-9])", r"Democrat Senator(?![A-Za-z0-9])", 
                   r"Dem Senator(?![A-Za-z0-9])", 
                   r"Republican Senators", r"Rep Senators", r"GOP Senators", r"Democratic Senators", r"Democrat Senators", r"Dem Senators", 
                   r"Sentencing Commission", r"Small Business Administration", r"Smithsonian Institution", 
                   r"Social Security Administration", r"Social Security Advisory Board", r"Southeastern Power Administration", 
                   r"Southern Command", r"Southwestern Power Administration", r"Space Command", r"Special Operations Command", 
                   r"State Department", r"State Justice Institute", r"Stennis Center for Public Service", r"Strategic Command", 
                   r"Substance Abuse and Mental Health Services Administration", r"Supreme Court", 
                   r"Supreme Court of the United States", r"Surface Transportation Board", r"Susquehanna River Basin Commission", 
                   r"Tax Court", r"Tennessee Valley Authority", r"Trade and Development Agency", r"Trade Representative", 
                   r"Transportation Command", r"Transportation Department", r"Transportation Security Administration", 
                   r"Treasury Department", r"Trustee Program", r"U\.S\. Access Board", r"U\.S\. Africa Command", r"U\.S\. Army", r"U\.S\. Armed Forces", r"US Armed Forces",
                   r"U\.S\. Departments", r"U\.S\. Mint", r"Udall Foundation", r"Under Secretary for Political Affairs", 
                   r"Under Secretary for Public Diplomacy and Public Affairs", r"Unified Combatant Commands", 
                   r"Uniformed Services University of the Health Sciences", r"United States Institute of Peace", r"US Access Board", 
                   r"US Africa Command", r"US Army", r"US Departments", r"US Mint", r"Veterans Affairs Department", 
                   r"Veterans Benefits Administration", r"Veterans' Employment and Training Service", 
                   r"Veterans Health Administration", r"Vice President", r"Voice of America", r"Wage and Hour Division", 
                   r"Washington Headquarters Services", r"Weather Service", r"West Point Military Academy", 
                   r"Western Area Power Administration", r"White House", r"Wireless Telecommunications Bureau", r"Women's Bureau", 
                   r"Woodrow Wilson International Center for Scholars"]

senate = r"(?<![A-Za-z0-9])Senate(?![A-Za-z0-9])(?!\s+(Republicans|Reps|Democrats|Dems|Majority Leader|Minority Leader))"

committees = [r"(?<!(?:Senate|House)\s+)Agriculture Committee",
              r"(?<!(?:Senate|House)\s+)Appropriations Committee",
              r"(?<!(?:Senate|House)\s+)Armed Services Committee",
              r"(?<!(?:Senate|House)\s+)Budget Committee",
              r"(?<!(?:Senate|House)\s+)Ethics Committee",
              r"(?<!(?:Senate|House)\s+)Joint Committee on Printing",
              r"(?<!(?:Senate|House)\s+)Joint Committee on Taxation",
              r"(?<!(?:Senate|House)\s+)Joint Committee on the Library",
              r"(?<!(?:Senate|House)\s+)Judiciary Committee",
              r"(?<!(?:Senate|House)\s+)Small Business Committee",
              r"(?<!(?:Senate|House)\s+)Veterans' Affairs Committee",
              r"(?<!(?:Senate|House)\s+)Ways and Means Committee",
              r"(?<!(?:Senate|House)\s+)Joint Economic Committee",
              r"(?:Senate\s+)Agriculture\, Nutrition\, and Forestry Committee",
              r"(?:Senate\s+)Banking\, Housing\, and Urban Affairs Committee",
              r"(?:Senate\s+)Commerce\, Science\, and Transportation Committee",
              r"(?:Senate\s+)Energy and Natural Resources Committee",
              r"(?:Senate\s+)Environment and Public Works Committee",
              r"(?:Senate\s+)Finance Committee",
              r"(?:Senate\s+)Foreign Relations Committee",
              r"(?:Senate\s+)Health\, Education\, Labor\, and Pensions Committee",
              r"(?:Senate\s+)Homeland Security and Governmental Affairs Committee",
              r"(?:Senate\s+)Indian Affairs Committee",
              r"(?:Senate\s+)Joint Committee of Congress on the Library",
              r"(?:Senate\s+)Joint Congressional Committee on Inaugural Ceremonies",
              r"(?:Senate\s+)Joint Select Committee on Solvency of Multiemployer Pension Plans",
              r"(?:Senate\s+)Rules and Administration Committee",
              r"(?:Senate\s+)Select Committee on Ethics",
              r"(?:Senate\s+)Select Committee on Intelligence", r"(?:Senate\s+)Intel(?:ligence)? Committee",
              r"(?:Senate\s+)Small Business(?:\s+and Entrepreneurship)? Committee",
              r"(?:Senate\s+)Special Committee on Aging",
              r"(?:House\s+)Education and Labor Committee",
              r"(?:House\s+)Energy and Commerce Committee",
              r"(?:House\s+)Financial Services Committee",
              r"(?:House\s+)Foreign Affairs Committee",
              r"(?:House\s+)Homeland Security Committee",
              r"(?:House\s+)House Administration Committee",
              r"(?:House\s+)House Administration(?:\s+|[-–]\s*)Freedom to Vote Act Committee",
              r"(?:House\s+)Natural Resources Committee",
              r"(?:House\s+)Oversight and Reform Committee",
              r"(?:House\s+)Permanent Select Committee on Intelligence Committee",
              r"(?:House\s+)Rules Committee",
              r"(?:House\s+)Science\, Space\, and Technology Committee",
              r"(?:House\s+)Select Committee on Climate Crisis",
              r"(?:House\s+)Select Committee on Economic Disparity and Fairness in Growth",
              r"(?:House\s+)Select Committee on the Modernization of Congress",
              r"(?:House\s+)Select Committee to Investigate the January 6th Attack on the U.S. Capitol",
              r"(?:House\s+)Select Committee to Investigate the January 6th Attack on the U.S. Capitol Report", r"(?:(?:January|Jan\.?)\s*6|1\/6)\s+(?:House\s+)?(?:select\s+)?committee",
              r"(?:House\s+)Select Subcommittee on the Coronavirus Crisis Committee",
              r"(?:House\s+)Transportation and Infrastructure Committee",
              r"(?:House\s+)Ways and Means(?:\s+|[-–]\s*)Green Book Committee",
              r"House(?:\s+select)?\s+Committee\b", r"Senate(?:\s+select)?\s+Committee\b"
              r"House(?:\s+select)?\s+Committees", r"Senate(?:\s+select)?\s+Committees"]

potential_state_institutions = [r"Agriculture Department", r"Attorney General", r"Assistant Attorney General", r"Cabinet", r"Chief Justice", r"Circuit Courts of Appeal", 
                                r"Court of Appeal", r"Courts of Appeal", r"Department of Agriculture", r"Commerce Department", r"Department of Commerce", r"Department of Defense", r"Energy Department", 
                                r"Department of Energy", r"Department of Health and Human Services", r"Department of Homeland Security", r"Department of Housing and Urban Development", r"Housing Office", r"Office of Housing",
                                r"Department of Interior", r"Department of Justice", r"Department of Labor", r"Department of State", r"Department of the Interior", r"Department of the Treasury", 
                                r"Department of Transportation", r"Transportation Department", r"Department of Treasury", r"Department of Veterans Affairs", r"Veterans Affairs Department", 
                                r"Department of Education", r"Education Department", r"Fire Administration", r"Health and Human Services Department", r"Homeland Security Department", r"Interior Department", r"Justice Department", 
                                r"Labor Department", r"Government(?![A-Za-z0-9])(?!\s?officials)", r"Government officials", r"(?<![A-Za-z0-9])Governors(?![A-Za-z0-9])", r"Head of department", r"Head of the department", r"House of Representatives", 
                                r"HouseDemocrats", r"House Democrats", r"HouseRepublicans", r"House Republicans", r"HouseGOP", r"Inspectors General", r"Labor Department", r"Medicaid", r"Office of Child Support Services",
                                r"Office for Civil Rights\, Department of Education", r"Office for Civil Rights\, Department of Health and Human Services", r"Office of Career\, Technical\, and Adult Education", 
                                r"Office of Child Support Enforcement", r"Office of Child Support Services", r"Office of Civil Rights\, Department of Education", r"Office of Community Planning and Development", 
                                r"Office of Disability Employment Policy", r"Office of Elementary and Secondary Education", r"Office of Energy Efficiency and Renewable Energy", r"Office of English Language Acquisition", 
                                r"Office of Environmental Management", r"Office of Fair Housing and Equal Opportunity", r"Office of Fossil Energy and Carbon Management", r"Office of Government Ethics", r"Office of Housing", 
                                r"Office of Immigrant and Employee Rights", r"Office of Investor Education and Advocacy", r"Office of Justice Programs", r"Office of Juvenile Justice and Delinquency Prevention", 
                                r"Office of Lead Hazard Control and Healthy Homes", r"Office of Management and Budget", r"Office of Manufactured Housing Programs", r"Office of Minority Health", 
                                r"Office of Multifamily Housing Programs", r"Office of Natural Resources Revenue", r"Office of Nuclear Energy", r"Office of Personnel Management", r"Office of Policy Development and Research",
                                r"Office of Postsecondary Education", r"Office of Refugee Resettlement", r"Office of Science and Technology Policy", r"Office of Scientific and Technical Information", r"Office of Servicemember Affairs", 
                                r"Office of Special Counsel", r"Office of Special Education and Rehabilitative Services", r"Office of Weights and Measures", r"Office on Violence Against Women",
                                r"Parole Commission", r"Secretary of State", r"Secretary of the Treasury", r"Treasury Department", r"Secretary of Defense", r"Secretary of the Interior", r"Secretary of Agriculture", r"Secretary of Commerce", 
                                r"Secretary of Labor", r"Secretary of Health and Human Services", r"Secretary of Housing and Urban Development", r"Secretary of Transportation", r"Secretary of Energy", 
                                r"Secretary of Education", r"Secretary of Veterans Affairs", r"Secretary of Homeland Security", r"Securities and Exchange Commission", 
                                r"(?<![A-Za-z0-9])(?<!(Republican|Rep|GOP|Democrat|Dem|Democratic)\s+)Senators(?![A-Za-z0-9])", 
                                r"Senate Majority Leader", r"SenateRepublicans", r"SenateReps", r"Senate Republicans", r"Senate Reps", r"SenateDemocrats", r"SenateDems", r"Senate Democrats", r"Senate Dems", 
                                r"Republican Senator(?![A-Za-z0-9])", r"Rep Senator(?![A-Za-z0-9])", r"GOP Senator(?![A-Za-z0-9])", r"Democratic Senator(?![A-Za-z0-9])", r"Democrat Senator(?![A-Za-z0-9])", 
                                r"Dem Senator(?![A-Za-z0-9])", r"Republican Senators", r"Rep Senators", r"GOP Senators", r"Democratic Senators", r"Democrat Senators", r"Dem Senators", r"State Department", 
                                r"Supreme Court", r"Tax Court", r'Fish and Wildlife Service', r'Food and Nutrition Service', r'Food Safety and Inspection Service', r'Geological Survey', r'Hour and Wage Division', r'Mediation and Conciliation Service',
                                r'Policy Development and Research', r'Sentencing Commission', r'Veterans Benefits Administration', r"Veterans' Employment and Training Service", r'Veterans Health Administration', r'Trade Representative',
                                r'Trustee Program']

senator = r"(?<![A-Za-z0-9])(?<!(Republican|Rep|GOP|Democrat|Dem|Democratic)\s+)Senator(?![A-Za-z0-9])"
governor = r"(?<![A-Za-z0-9])(?<!(Republican|Rep|GOP|Democrat|Dem|Democratic)\s+)Governor(?![A-Za-z0-9])"
legislator = [r"Congressman", r"Congresswoman"]

congress_members =  [r"Kwanza Hall", r"Chris Jacobs", r"Kevin McCarthy", r"Justin Amash", r"Mike Garcia", r"Kweisi Mfume", r"Mac Thornberry", r"Steny Hoyer", r"Devin Nunes", r"Steve Scalise", r"Martha Roby", r"Trey Hollingsworth",
                    r"Virginia Foxx", r"Harold Rogers", r"Hal Rogers", r"Patrick McHenry", r"Rob Woodall", r"Thomas Tiffany", r"Kay Granger", r"Gary Palmer",
                    r"Jim Jordan", r"Thomas Massie", r"John(?:\s+[A-Z][A-Za-z.]+)?\s+Rose", r"Kevin Brady", r"John(?:\s+[A-Z][A-Za-z.]+)?\s+Carter", r"Russ Fulcher", r"Garret Graves", r"Robert Aderholt",
                    r"Sam Graves", r"Daniel Webster", r"Dan Bishop", r"Mike Rogers", r"Warren Davidson", r"Michael Simpson", r"Mike Simpson", r"Steve Womack",
                    r"Clay Higgins", r"Greg Walden", r"Greg Pence", r"Rob Bishop", r"George Holding", r"Tom Rice", r"Michael Cloud", r"Ron Estes",
                    r"James Clyburn", r"Jim Clyburn", r"Bryan Steil", r"John Shimkus", r"Chip Roy", r"Gregory Murphy", r"Doug Collins", r"Liz Cheney",
                    r"Michael Conaway", r"Jodey Arrington", r"Tom McClintock", r"Frank Lucas", r"Ken Buck", r"Dusty Johnson", r"Mike Johnson", r"Austin Scott",
                    r"Drew Ferguson", r"Tim Walberg", r"Roger Williams", r"Barry Loudermilk", r"Vern Buchanan", r"Kelly Armstrong", r"Ralph Abraham", r"William Timmons",
                    r"Kenny Marchant", r"Bill Huizenga", r"Morgan Griffith", r"Mark(?:\s+[A-Z][A-Za-z.]+)?\s+Green", r"Mark Amodei", r"Adrian Smith", r"Scott DesJarlais",
                    r"Larry Bucshon", r"Tim Burchett", r"David Kustoff", r"Steven Palazzo", r"James Comer", r"Jamie Comer", r"Fred Keller", r"Stacey Plaskett", r"Michael Burgess",
                    r"Jack Bergman", r"Jaime Herrera Beutler", r"Neal Dunn", r"Mark Walker", r"Brett Guthrie", r"Carol Miller", r"Daniel Meuser", r"Michael Guest",
                    r"Mo Brooks", r"James Sensenbrenner", r"Ben McAdams", r"Louie Gohmert", r"Lloyd Smucker", r"Ben Cline", r"Bruce Westerman", r"Tom Reed",
                    r"Charles Fleischmann", r"Chuck Fleischmann", r"Billy Long", r"Jason Smith", r"Francis Rooney", r"Chris Stewart", r"Darin LaHood", r"Andy Harris",
                    r"Mario Diaz-Balart", r"French Hill", r"Aumua Amata Radewagen", r"Peter Visclosky", r"Tom Emmer", r"Ken Calvert", r"Trent Kelly", r"James Baird",
                    r"Paul Mitchell", r"Earl Carter", r"Buddy Carter", r"Garland Barr", r"Andy Barr", r"Brad Wenstrup", r"John Moolenaar", r"Bill Johnson",
                    r"Joe Cunningham", r"Richard Neal", r"Bradley Byrne", r"Rick Allen", r"Blaine Luetkemeyer", r"Robert Latta", r"Greg Gianforte", r"John Curtis", r"Dan Newhouse", r"Eric Crawford",
                    r"Rick Crawford", r"Richard Hudson", r"Steve King", r"Fred Upton", r"Adam Kinzinger", r"David Schweikert", r"Markwayne Mullin", r"Jeff Fortenberry",
                    r"Jeff Duncan", r"John Joyce", r"Lance Gooden", r"David Rouzer", r"Kurt Schrader", r"Scott Perry", r"Kevin Hern", r"Doug Lamborn",
                    r"Andy Biggs", r"Will Hurd", r"Mike Bost", r"Ross Spano", r"Robert Wittman", r"Michael McCaul", r"Jim Hagedorn", r"Anthony Gonzalez",
                    r"Michael Waltz", r"Jody Hice", r"Michael Turner", r"Jared Golden", r"Bob Gibbs", r"Collin Peterson", r"David Loebsack", r"Susan Brooks",
                    r"Lloyd Doggett", r"Glenn Thompson", r"Mike Gallagher", r"Christopher Smith", r"Chris Smith", r"Lizzie Fletcher", r"Pete Stauber", r"Gregorio Sablan",
                    r"Donald Norcross", r"Hakeem Jeffries", r"Scott Tipton", r"Dan Crenshaw", r"Nita Lowey", r"Lee Zeldin", r"Xochitl Torres Small", r"Jenniffer González-Colón", 
                    r"Jenniffer Gonzalez-Colon", r"Bill Flores", r"Brian Babin", r"Raul Ruiz", r"Pete Olson",
                    r"Steven Watkins", r"Mike Kelly", r"Jackie Walorski", r"Greg Stanton", r"David Roe", r"Phil Roe", r"Glenn Grothman", r"David Joyce",
                    r"Joe Wilson", r"Lucy McBath", r"Steve Chabot", r"Brian Mast", r"Jim Banks", r"Ann Wagner", r"Doug LaMalfa", r"Sharice Davids",
                    r"Robert Scott", r"Bobby Scott", r"Lois Frankel", r"Van Taylor", r"Donald McEachin", r"Colin Allred", r"Conor Lamb", r"John Rutherford",
                    r"David McKinley", r"Kim Schrier", r"Antonio Delgado", r"Debbie Lesko", r"Troy Balderson", r"Guy Reschenthaler", r"Lauren Underwood", r"Joaquin Castro",
                    r"Maxine Waters", r"Katherine Clark", r"Denver Riggleman", r"Cathy Anne McMorris Rodgers", r"Cathy Anne Rodgers", r"Cathy McMorris Rodgers", r"Ron Wright", r"John Sarbanes", 
                    r"Alexander Mooney", r"Cedric Richmond",
                    r"Vicky Hartzler", r"Ted Yoho", r"Cheri Bustos", r"Gus Bilirakis", r"Norma Torres", r"Henry Cuellar", r"Ted Budd", r"John Yarmuth", r"Jennifer Wexton", r"Marc Veasey",
                    r"Al Green", r"Jimmy Gomez", r"Ami Bera", r"Susie Lee", r"Mikie Sherrill", r"Randy Weber", r"Bill Posey", r"Kendra Horn",
                    r"George Butterfield", r"G\.K\. Butterfield", r"Anthony Brindisi", r"William(?:\s+[A-Z][A-Za-z.]+)?\s+Keating", r"Bradley Schneider", r"Brad Schneider", r"Haley Stevens",
                    r"Paul Gosar", r"Joe Courtney", r"Stephanie Murphy", r"Don Young", r"Matt Gaetz", r"John Katko", r"Frank Pallone", r"Gregory Steube",
                    r"Daniel Lipinski", r"Steven Horsford", r"Filemon Vela", r"Rick Larsen", r"Ralph Norman", r"Ann Kirkpatrick", r"David Scott", r"John Larson",
                    r"David Price", r"Bill Pascrell", r"Michael Doyle", r"Rodney Davis", r"Steve Stivers", r"Alma Adams", r"Michael San Nicolas", r"Doris Matsui",
                    r"Mike Levin", r"Abby Finkenauer", r"Pete Aguilar", r"Tom O'Halleran", r"Peter King", r"Pete King", r"Chrissy Houlahan", r"Ron Kind",
                    r"A\. Dutch Ruppersberger", r"Lori Trahan", r"Luis Correa", r"James Himes", r"Jim Himes", r"Sean Casten", r"Jason Crow", r"Rosa DeLauro",
                    r"Tulsi Gabbard", r"Charlie Crist", r"James Langevin", r"Jim Langevin", r"Marcia Fudge", r"Don Bacon", r"Mike Thompson", r"Brenda Lawrence", r"Diana DeGette", r"Al Lawson", 
                    r"Josh Gottheimer", r"Jim Cooper",
                    r"Val Demings", r"Katie Porter", r"Donna Shalala", r"Adam Schiff", r"Raja Krishnamoorthi", r"(?<![A-Za-z0-9])Ed Perlmutter", r"José Serrano", r"Jose Serrano", r"Sylvia Garcia",
                    r"Brendan Boyle", r"Lacy Clay", r"Sanford Bishop", r"Debbie Mucarsel-Powell", r"Marcy Kaptur", r"Emanuel Cleaver", r"Andy Kim", r"Jerry McNerney",
                    r"Brian Higgins", r"Veronica Escobar", r"Elise Stefanik", r"Juan Vargas", r"Linda Sánchez", r"Linda Sanchez", r"Denny Heck", r"Jim Costa", r"Max Rose",
                    r"Andy Levin", r"Susan Davis", r"Elissa Slotkin", r"Daniel Kildee", r"Tom Malinowski", r"Joseph Morelle", r"Anthony Brown", r"Alexandria Ocasio-Cortez",
                    r"Dina Titus", r"Matthew Cartwright", r"Matt Cartwright", r"Scott Peters", r"Robin Kelly", r"Dwight Evans", r"Angie Craig", r"Seth Moulton",
                    r"Mike Quigley", r"Vicente Gonzalez", r"Eric Swalwell", r"Dean Phillips", r"Eliot Engel", r"Madeleine Dean", r"Eddie Bernice Johnson", r"Tom Cole", r"Sean Maloney", 
                    r"John Garamendi", r"Suzan DelBene",
                    r"Donald Beyer", r"Jackie Speier", r"Kathleen Rice", r"Debbie Wasserman Schultz", r"Mark Takano", r"Abigail Spanberger", r"Theodore Deutch", r"Ted Deutch",
                    r"Karen Bass", r"Brad Sherman", r"Elaine Luria", r"Jefferson Van Drew", r"Stephen Lynch", r"Cynthia Axne", r"Carolyn Maloney", r"Jerrold Nadler",
                    r"Kathy Castor", r"Nanette Barragán", r"Nanette Barragan", r"Bill Foster", r"Adam Smith", r"Mary Gay Scanlon", r"Paul Tonko", r"Salud Carbajal", r"TJ Cox",
                    r"Terri Sewell", r"Danny Davis", r"Chris Pappas", r"Gregory Meeks", r"Gerald Connolly", r"(?<![A-Za-z0-9])Ed Case(?![A-Za-z0-9])", r"Anna Eshoo", r"Donald Payne Jr\.",
                    r"Harley Rouda", r"Lisa Blunt Rochester", r"Frederica Wilson", r"Ayanna Pressley", r"Ruben Gallego", r"Rashida Tlaib", r"Tim Ryan", r"Jimmy Panetta",
                    r"Ilhan Omar", r"Betty McCollum", r"Debbie Dingell", r"Joe Neguse", r"Joseph(?:\s+[A-Z][A-Za-z.]+)?\s+Kennedy",
                    r"Suzanne Bonamici", r"rusan Wild", r"Lucille Roybal-Allard", r"Josh Harder", r"Bennie Thompson", r"Peter DeFazio", r"Jared Huffman", r"Tony Cárdenas", r"Tony Cardenas",
                    r"Jesús García", r"Chuy García", r"Jesus Garcia", r"Chuy Garcia", r"Albio Sires", r"Mark DeSaulnier", r"Joyce Beatty", r"Pramila Jayapal", r"Judy Chu", r"Peter Welch",
                    r"Grace Meng", r"Nydia Velázquez", r"Nydia Velazquez", r"Henry C\. Johnson", r"Hank Johnson", r"Julia Brownley", r"Derek Kilmer", r"Zoe Lofgren", r"Ted Lieu",
                    r"Jahana Hayes", r"David Cicilline", r"Chellie Pingree", r"Bonnie Watson Coleman", r"Thomas Suozzi", r"Adriano Espaillat", r"Gilbert Cisneros", r"Ann Kuster",
                    r"Bobby Rush", r"David Trone", r"André Carson", r"Andre Carson", r"Yvette Clarke", r"Mark Pocan", r"Gwen Moore", r"Debra Haaland", r"Earl Blumenauer",
                    r"Grace Napolitano", r"Alan Lowenthal", r"Darren Soto", r"Ro Khanna", r"Janice Schakowsky", r"Jan Schakowsky", r"Raúl Grijalva", r"Raul Grijalva", r"Barbara Lee",
                    r"Alcee Hastings", r"James McGovern", r"Jim McGovern", r"Sheila Jackson Lee", r"Jamie Raskin", r"Steve Cohen", r"Brian Fitzpatrick", r"Eleanor Holmes Norton",
                    r"Rudy Yakym", r"Joseph Sempolinski", r"Mary Peltola", r"Patrick Ryan", r"Mike Flood", r"Connie Conway", r"Mayra Flores", r"Brad Finstad",
                    r"Mike Carey", r"Cliff Bentz", r"Victoria Spartz", r"Troy Nehls", r"Julia Letlow", r"Ernest Gonzales", r"Tony Gonzales", r"Scott Fitzgerald",
                    r"Marjorie Taylor Greene", r"Michelle Fischbach", r"Andrew Clyde", r"Blake Moore", r"Michelle Steel", r"Jerry Carl", r"Darrell Issa", r"Jake Ellzey",
                    r"Matthew Rosendale", r"Frank Mrvan", r"Jay Obernolte", r"Sheila Cherfilus-McCormick", r"Beth Van Duyne", r"Lisa McClain", r"August Pfluger", r"Shontel Brown",
                    r"Troy Carter", r"Randy Feenstra", r"Patrick Fallon", r"Pat Fallon", r"Stephanie Bice", r"Pete Sessions", r"Diana Harshbarger", r"Carolyn Bourdeaux",
                    r"Katherine Cammack", r"Kat Cammack", r"Jacob LaTurner", r"Jake LaTurner", r"Barry Moore", r"Teresa Leger Fernandez", r"Carlos Gimenez", r"Clarence Owens",
                    r"Burgess Owens", r"Nicole Malliotakis", r"Scott Franklin", r"Peter Meijer", r"Nancy Mace", r"Lauren Boebert", r"David Valadao", r"Ashley Hinson",
                    r"Cori Bush", r"Yvette Herrell", r"Madison Cawthorn", r"Robert Good", r"Bob Good", r"Claudia Tenney", r"Young Kim", r"Byron Donalds",
                    r"Tracey Mann", r"Melanie Stansbury", r"Mary Miller", r"Ronny Jackson", r"Kathy Manning", r"Andrew Garbarino", r"Kaiali'i Kahele", r"Ritchie Torres",
                    r"Jake Auchincloss", r"Maria Salazar", r"Mariannette Miller-Meeks", r"Marilyn Strickland", r"Sara Jacobs", r"Jamaal Bowman", r"Deborah Ross", r"Marie Newman",
                    r"Mondaire Jones", r"Nikema Williams", r"Martha McSally"]

senators = [r"Mark Kelly", r"Richard Shelby", r"Mitch McConnell", r"Benjamin Sasse", r"Ben Sasse", r"Patrick Toomey", r"Pat Toomey", r"Ron Johnson", r"Rand Paul", r"Mitt Romney", r"Richard Burr", r"John Thune", 
            r"Michael Enzi", r"Mike Lee", r"Lamar Alexander", r"Lindsey Graham", r"Kelly Loeffler", r"Joshua Hawley", r"Josh Hawley", r"Deb Fischer", r"John Neely Kennedy", r"Michael Crapo", r"Mike Crapo", 
            r"John Barrasso", r"Charles Grassley", r"Chuck Grassley", r"James Risch", r"Pat Roberts", r"Tim Scott", r"John Hoeven", r"Roy Blunt", r"James Inhofe", r"Jim Inhofe", r"David Perdue", r"Bill Cassidy", 
            r"Rick Scott", r"Robert Portman", r"Rob Portman", r"Ted Cruz", r"Tom Cotton", r"James Lankford", r"Jerry Moran", r"Charles Schumer", r"Chuck Schumer", r"Mike Rounds", r"Cindy Hyde-Smith", 
            r"Dan Sullivan", r"Roger Wicker", r"Joe Manchin", r"Cory Gardner", r"Brian Schatz", r"Todd Young", r"Lisa Murkowski", r"Maria Cantwell", r"Steve Daines", r"Mark Warner", 
            r"Tom Udall", r"Martin Heinrich", r"John Cornyn", r"John Boozman", r"Mike Braun", r"Joni Ernst", r"Thomas Carper", r"Marsha Blackburn", r"Jon Tester", r"Thom Tillis", 
            r"Patrick Leahy", r"Shelley Moore Capito", r"Patty Murray", r"Marco Rubio", r"Debbie Stabenow", r"Christopher Murphy", r"Robert Menendez", r"Bob Menedez", r"Michael Bennet", 
            r"Kevin Cramer", r"Timothy Kaine", r"Tim Kaine", r"John(?:\s+[A-Z][A-Za-z.]+)?\s+Reed", r"Jack(?:\s+[A-Z][A-Za-z.]+)?\s+Reed", r"Kyrsten Sinema", r"Angus King", r"Doug Jones", r"Catherine Cortez Masto", r"Sheldon Whitehouse", 
            r"Bernard Sanders", r"Bernie Sanders", r"Gary Peters", r"Susan Collins", r"Robert Casey", r"Bob Casey", r"Jacky Rosen", r"Mazie Hirono", r"Benjamin Cardin", r"Jeanne Shaheen", r"Tammy Duckworth", 
            r"Margaret Hassan", r"Maggie Hassan", r"Christopher Coons", r"Tammy Baldwin", r"Richard Durbin", r"Ron Wyden", r"Sherrod Brown", r"Dianne Feinstein", r"Kamala Harris", r"Tina Smith", 
            r"Kirsten Gillibrand", r"Elizabeth Warren", r"Cory Booker", r"Jeff Merkley", r"Edward Markey", r"(?<![A-Za-z0-9])Ed Markey", r"Chris Van Hollen", r"Amy Klobuchar", r"Richard Blumenthal", r"Tommy Tuberville", 
            r"John Hickenlooper", r"Jon Ossoff", r"Bill Hagerty", r"Cynthia Lummis", r"Roger Marshall", r"Raphael Warnock", r"Ben Ray Luján", r"Alejandro Padilla", r"Alex Padilla"]

cabinet_members = [r"Tom Price", r"John(?:\s+[A-Z][A-Za-z.]+)?\s+Kelly", r"Reince Priebus", r"Rex Tillerson", r"Jeff Sessions", r"David Shulkin", r"Scott Pruitt", r"Nikki Haley", r"Jim Mattis", 
                   r"Ryan Zinke", r"Alexander Acosta", r"Rick Perry", r"Kirstjen Nielsen", r"Dan Coats", r"Linda McMahon", r"Mick Mulvaney", 
                   r"Steven Mnuchin", r"Sonny Perdue", r"Wilbur Ross", r"Ben Carson", r"Elaine Chao", r"Betsy DeVos", r"Robert Lighthizer", r"Mike Pompeo", r"Alex Azar", r"Robert Wilkie", 
                   r"Andrew Wheeler", r"Gina Haspel", r"Mark Esper", r"William Barr", r"David Bernhardt", r"Eugene Scalia", r"Dan Brouillette", r"Chad Wolf", r"Kelly Craft", r"Christopher(?:\s+[A-Z][A-Za-z.]+)?\s+Miller", 
                   r"a(?:\s+[A-Z][A-Za-z.]+)?\s+Rosen", r"Russell Vought", r"John Ratcliffe", r"Jovita Carranza", r"Mark Meadows", r"Eric Lander", r"Marty Walsh", r"Cecilia Rouse", r"Ron Klain", r"Marcia Fudge", 
                   r"Michael(?:\s+[A-Z][A-Za-z.]+)?\s+Regan", r"Antony Blinken", r"Janet Yellen", r"Lloyd Austin", r"Merrick Garland", r"Deb Haaland", r"Tom Vilsack", r"Gina Raimondo", 
                   r"Xavier Becerra", r"Pete Buttigieg", r"Jennifer Granholm", r"Miguel Cardona", r"Denis McDonough", r"Alejandro Mayorkas", r"Shalanda Young", r"Avril Haines", r"William(?:\s+[A-Z][A-Za-z.]+)?\s+Burns", 
                   r"Katherine Tai", r"Linda Thomas-Greenfield", r"Isabel Guzman", r"Arati Prabhakar", r"Julie Su", r"Jared Bernstein", r"Jeff Zients", r"Adrianne Todman", r"Jane Nishida"]

governors = [r"Eric Holcomb", r"John Carney", r"John Bel Edwards", r"Bruce Rauner", r"Doug Ducey", r"Asa Hutchinson", r"Larry Hogan", 
             r"Charlie Baker", r"David Ige", r"Phil Bryant", r"Mike Parson", r"Chris Sununu", r"Roy Cooper", r"Kristi Noem", r"Jay Inslee", 
             r"Jim Justice", r"Doug Burgum", r"Pete Ricketts", r"Steve Sisolak", r"Kate Brown", r"Tom Wolf", r"Ralph Northam", r"Steve Bullock", 
             r"Greg Gianforte", r"Gina Raimondo", r"Dan McKee", r"Gary Herbert", r"Spencer Cox", r"Phil Bryant", r"Tate Reeves", r"Gavin Newsom", 
             r"Jared Polis", r"Ned Lamont", r"Ron DeSantis", r"Brian Kemp", r"Brad Little", r"J\.B\. Pritzker", r"JB Pritzker", r"Laura Kelly", r"Andy Beshear", 
             r"Janet Mills", r"Gretchen Whitmer", r"Tim Walz", r"Michelle Lujan Grisham", r"Kathy Hochul", r"Mike DeWine", r"Kevin Stitt", 
             r"Bill Lee", r"Tony Evers", r"Mark Gordon", r"Mike Dunleavy", r"Phil Murphy", r"Kay Ivey", r"Kim Reynolds", r"Henry McMaster", 
             r"Phil Scott", r"Greg Abbott", r"Andrew(?:\s+[A-Z][A-Za-z.]+)?\s+Cuomo"]

supreme_justices = [r"John Roberts", r"Clarence Thomas", r"Samuel Alito", r"Sonia Sotomayor", r"Elena Kagan", r"Neil Gorsuch", r"Brett Kavanaugh", 
                    r"Ruth Bader Ginsburg", r"Amy Coney Barrett", r"Stephen Breyer", r"Ketanji Brown Jackson"]

other_politicians = [r"Christopher(?:\s+[A-Z][A-Za-z.]+)?\s+Wray", r"Bill Barr", r"(?:Postmaster(?:\s+General)?\s+)?(?:Megan\s+)?Brennan", r"(?:Postmaster(?:\s+General)?\s+)?(?:Louis\s+)?DeJoy"]

unambiguous_politicians = [r"Donald Trump(?!\s?(Sr|Jr|tower))", r"Donald John Trump", r"Donald J Trump(?!\s?(Sr|Jr|tower))", r"Donald J\. Trump(?!\s?(Sr|Jr|tower))", 
                           r"Joe Biden", r"Mike Pence", r"Nancy Pelosi", r"Bernie Sanders", r"Kamala Harris", r"Anthony S\. Fauci", r"Anthony Fauci", r"Dr\. Fauci", r"Dr Fauci"]

aliases_politicians = [r"(?<![A-Za-z0-9])Sleepy Joe(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])Crazy Nancy(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])Nervous Nancy(?![A-Za-z0-9])", 
                       r"(?<![A-Za-z0-9])Notorious RBG(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])Shifty Schiff(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])Mayor Pete(?![A-Za-z0-9])", 
                       r"(?<![A-Za-z0-9])Sleepy Kamala(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])Kamikaze Kamala(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])Moscow Mitch(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])MoscowMitch(?![A-Za-z0-9])"]

aliases_short = [r"(?<![A-Za-z0-9@])AOC(?![A-Za-z0-9])", r"(?<![A-Za-z0-9@])MTG(?![A-Za-z0-9])", r"(?<![A-Za-z0-9@])RBG(?![A-Za-z0-9])"]

surnames_only = [r"(?<![A-Za-z0-9])(?<!(Fred|Friedrich|Frederick|Mary\s?L?|Melania|Ivana|Ivanka|Eric|Tiffany|Marla|Barron)\s+)Trump(?!\s?(Sr|Jr|tower))(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])(?<!(Jill|Hunter|Beau|Ashley|Hallie)\s+)Biden(?![A-Za-z0-9])",
                 r"(?<![A-Za-z0-9])Pence(?![A-Za-z0-9])", r"(?<![A-Za-z0-9]|Senator\s+|Andy\s+)Harris(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])Pelosi(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])Bernie(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])Sanders(?![A-Za-z0-9])",
                 r"(?<![A-Za-z0-9])Kamala(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])Fauci(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])DeSantis(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])Mnuchin(?![A-Za-z0-9])"]

title_combos = [r"(?:President(?:-elect)?|@?POTUS(?:-elect)?)\s+(?:Donald(?:\s+John|\s+J\.?)?\s+Trump|Trump|@realdonaldtrump)",
                r"(?:President(?:-elect)?|@?POTUS(?:-elect)?)\s+(?:Joe\s+Biden|Biden|@JoeBiden)",
                r"(?:Vice President(?:-elect)?|@?VPOTUS|@?VP(?:-elect)?)\s+(?:Mike\s+Pence|Pence|@Mike_Pence)",
                r"(?:Vice President(?:-elect)?|@?VPOTUS|Senator|@?VP(?:-elect)?)\s+(?:Kamala\s+Harris|Harris|@KamalaHarris)",
                r"Speaker Pelosi", r"Biden Admin(?:istration)?", r"Trump Admin(?:istration)?"]

combo_handles = [r"@VP(?![A-Za-z0-9])", r"@POTUS(?![A-Za-z0-9])", r"@realdonaldtrump", r"@JoeBiden", r"@Mike_Pence", r"@KamalaHarris"]

abbreviations = [r"(?<![A-Za-z0-9])POTUS(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])POTUS(?:[-\u2013\u2014]?elect)?(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])VP(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])VPOTUS(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])SCOTUS(?![A-Za-z0-9])", 
                 r"(?<![A-Za-z0-9])DOJ(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])DOD(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])DHS(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])Treasury(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])Fed(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])EPA(?![A-Za-z0-9])", 
                 r"(?<![A-Za-z0-9])CDC(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])FDA(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])FBI(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])CIA(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])NIAID(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])NSA(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])NASA(?![A-Za-z0-9])"
                 r"(?<![A-Za-z0-9])NAVY(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])SEC(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)FCC(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)NIH(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])OSHA(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)USDA(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)USPS(?![A-Za-z0-9])",
                 r"(?<![A-Za-z0-9])ATF(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])SBA(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])HoR(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])HHS(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)CBP(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)TSA(?![A-Za-z0-9])",
                 r"(?:(?<![A-Za-z0-9])|@)FEMA(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)USCG(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)USMC(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)NOAA(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)NWS(?![A-Za-z0-9])",
                 r"(?:(?<![A-Za-z0-9])|@)GSA(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)DEA(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)FTC(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)CFTC(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)CFPB(?![A-Za-z0-9])",
                 r"(?:(?<![A-Za-z0-9])|@)NLRB(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)CBP(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)EEOC(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)OCC(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)FDIC(?![A-Za-z0-9])",
                 r"(?:(?<![A-Za-z0-9])|@)NIOSH(?![A-Za-z0-9])",r"(?:(?<![A-Za-z0-9])|@)USPHS(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)DOT(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)FAA(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)FRA(?![A-Za-z0-9])",
                 r"(?:(?<![A-Za-z0-9])|@)FHWA(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)NHTSA(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)IRS(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)DOS(?![A-Za-z0-9])",
                 r"(?:(?<![A-Za-z0-9])|@)USAID(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)BLS(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)BEA(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)USGS(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)USACE(?![A-Za-z0-9])",
                 r"(?:(?<![A-Za-z0-9])|@)HUD(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)MCCS(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)HRSA(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)CMS(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)CEA(?![A-Za-z0-9])",
                 r"(?:(?<![A-Za-z0-9])|@)CBO(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)OIRA(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)CRS(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)NIFA(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)FSIS(?![A-Za-z0-9])"
                 r"(?:(?<![A-Za-z0-9])|@)APHIS(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)FWS(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)OIG(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)ODNI(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)NRO(?![A-Za-z0-9])",
                 r"(?:(?<![A-Za-z0-9])|@)NGA(?![A-Za-z0-9])", r"(?:(?<![A-Za-z0-9])|@)USCIS(?![A-Za-z0-9])"]

twitter_handles_politicians = [r"@RepJoshG", r"@PeterMeijer", r"@RepJackBergman", r"@RobWittman", r"@RepMGriffith", r"@mtgreenee", r"@JudgeCarter", r"@RepBonamici", r"@RepEBJ", r"@marygayscanlon", r"@McGovernMA", r"@RepRonEstes", r"@USAttyBishop", r"@RepMeuser", r"@RepGilCisneros", r"@RepRooney", 
                               r"@RepCarbajal", r"@AdamKinzinger", r"@MoBrooks", r"@Nanette4CA", r"@RepBrianFitz", r"@SpeakerMcCarthy", r"@AndrewRWheeler", r"@RepMaryMiller", r"@RepMarkGreen", r"@GovStitt", r"@RepTroyCarter", r"@PhilBryantMS", r"@RepKevinBrady", r"@EleanorNorton", r"@Jim_Banks", r"@RepJimBanks", 
                               r"@RepBradWenstrup", r"@RepDustyJohnson", r"@RepJasonCrow", r"@jeffsessions", r"@RepNewhouse", r"@RepShontelBrown", r"@MichelleSteelCA", r"@RepMoolenaar", r"@RepPaulMitchell", r"@RepBillJohnson", r"@RepKathyManning", r"@DrMarkGreen4TN", r"@RepMarcyKaptur", r"@NydiaVelazquez", 
                               r"@EricLander46", r"@RepMarthaRoby", r"@RepJohnDuncanJr", r"@BrownforMD", r"@PoseyCampaign", r"@RepWalberg", r"@RepPatFallon", r"@RepDavidTrone", r"@GraceNapolitano", r"@MarkWalkerNC", r"@RepJerryCarl", r"@RepDeSaulnier", r"@RepChuck", r"@kwanzahall", r"@SteveScalise", 
                               r"@jimcoopertn", r"@RepRaulRuizMD", r"@RepWesterman", r"@JahanaHayesCT", r"@RepBarryMoore", r"@GovLarryHogan", r"@barrforsenate", r"@GovHerbert", r"@RepStenyHoyer", r"@RepPeterDeFazio", r"@SecretaryPete", r"@RepRonKind", r"@GovMikeDeWine", r"@GovDanMcKee", r"@Bethvanduyne", 
                               r"@RepSpanberger", r"@MikieSherrill", r"@TomColeOK04", r"@KenCalvert", r"@TulsiGabbard", r"@RepAdrianSmith", r"@RepHuizenga", r"@MickMulvaneyOMB", r"@RepRutherfordFL", r"@RepHalRogers", r"@RepElaineLuria", r"@DonBeyerVA", r"@BurgessOwens", r"@CongMikeSimpson", r"@JuliaBrownley26", 
                               r"@michaelcburgess", r"@RepBonnie", r"@Bonnie4Congress", r"@RepDerekKilmer", r"@GovLauraKelly", r"@CongBillPosey", r"@RepRichHudson", r"@CartwrightPA", r"@CuellarCampaign", r"@FSWInTheHouse", r"@RepPeteAguilar", r"@RepWexton", r"@RepJudyChu", r"@TimRyan", r"@RepJohnYarmuth", 
                               r"@RepMarkTakano", r"@RepStricklandWA", r"@RepAmata", r"@Michelle4NM", r"@DorisMatsui", r"@GregForMontana", r"@SecBlinken", r"@BryanSteil", r"@RepHartzler", r"@SecBernhardt", r"@TroyNehls", r"@RonEstesKS", r"@BenRayLujan", r"@RepBera", r"@CollinsforGA", 
                               r"@Congressman_JVD", r"@RepPeteKing", r"@RepJohnJoyce", r"@RepHoulahan", r"@DonnaShalala", r"@RepGallagher", r"@markpocan", r"@RepFilemonVela", r"@RepAdamSchiff", r"@RepTrentKelly", r"@RepBarbaraLee", r"@hinsonashley", r"@RepCartwright", r"@JenniferWexton", r"@RepHerrell", 
                               r"@RepAnnWagner", r"@RepJoeNeguse", r"@RepJoeMorelle", r"@TomWolfPA", r"@RepJacobs", r"@PeteSessions", r"@BettyMcCollum04", r"@AnthonyBrownMD4", r"@cliffbentz", r"@WilliamBarr", r"@Linda_McMahon", r"@WillHurd", r"@MikeLevin", r"@USRepGaryPalmer", r"@CurtisUT", r"@MarcVeasey", 
                               r"@GovArmstrong", r"@RepBrianHiggins", r"@RepCindyAxne", r"@MarkMeadows", r"@GrangerCampaign", r"@ChrisPappasNH", r"@RobinLynneKelly", r"@repdinatitus", r"@CongBoyle", r"@RepSlotkin", r"@RepJamesClyburn", r"@RepTomSuozzi", r"@RepSempolinski", r"@MikeKellyPA", r"@JasonCrowCO", 
                               r"@TonyGonzales4TX", r"@RepMcNerney", r"@RonaldKlain", r"@RepEscobar", r"@econjared46", r"@JayInslee", r"@henrymcmaster", r"@GuamCongressman", r"@vgescobar", r"@RepLawrence", r"@RepAlLawsonJr", r"@RepAnnaEshoo", r"@marty_walsh", r"@Rep_Clyde", r"@RepBrendanBoyle", r"@RepJuanVargas", 
                               r"@RepTonyGonzales", r"@HerreraBeutler", r"@CeciliaERouse", r"@DPrice4Congress", r"@RepRiggelman", r"@SuzanDelBene", r"@RepAlexMooney", r"@NitaLowey", r"@JoeCunninghamSC", r"@RepScottPeters", r"@RepJuliaLetlow", r"@GovernorLittle", r"@RonDeSantisFL", r"@CheriBustos", r"@AOC", 
                               r"@BetsyDeVosED", r"@DrNealDunnFL2", r"@reptrey", r"@repgregwalden", r"@FrenchHillAR", r"@RodneyDavis", r"@RepDougCollins", r"@Andy_Levin", r"@repjohnlewis", r"@LeaderHoyer", r"@katieporterca", r"@SenMcNerney", r"@GOPMajorityWhip", r"@Axne4Congress", r"@DanCrenshawTX", r"@RepJeffVanDrew", 
                               r"@BradSchneider", r"@RepConnieConway", r"@Sheila4Congress", r"@RepScottPerry", r"@RepLowenthal", r"@RepAndyLevin", r"@RepKayGranger", r"@RepCohen", r"@RepSteveWatkins", r"@RosenJeffrey", r"@BobbyScott", r"@ColPaulCookRet", r"@CongPalazzo", r"@RubenGallego", r"@EsperDoD", r"@DougBurgum", 
                               r"@GovChrisSununu", r"@VernBuchanan", r"@MikeDeWine", r"@RepDonBeyer", r"@BuckForColorado", r"@Victoria_Spartz", r"@CoriBush", r"@RepMaxineWaters", r"@GovernorVA", r"@RepHorsford", r"@TeamVisclosky", r"@RepChrisSmith", r"@JodyHiceFRCA", r"@YoungKimCA", r"@TomEmmer", 
                               r"@Liz_Cheney", r"@ScottFranklinFL", r"@JenGranholm", r"@RepWalterJones", r"@JohnCarneyDE", r"@NMalliotakis", r"@jahimes", r"@OregonGovBrown", r"@RepRickLarsen", r"@RajaForIL", r"@MikeGarciaCA27", r"@RepChrisPappas", r"@sharicedavids", r"@RepRudyYakym", r"@RepGregoryMeeks", 
                               r"@ScottPetersSD", r"@SeanDuffyWI", r"@GovTimWalz", r"@RepArrington", r"@jaredpolis", r"@TomOHalleran", r"@Ed4Colorado", r"@LtGovDennyHeck", r"@chiproytx", r"@RalphNorman", r"@Carolyn4GA7", r"@DwightEvansPA", r"@Schneider4IL10", r"@RepDeanPhillips", r"@MikeforWI", 
                               r"@Jim_Jordan", r"@AdrianneTodman", r"@RepDaveJoyce", r"@RepHankJohnson", r"@RepFinstad", r"@LloydDoggettTX", r"@SenPeterWelch", r"@valdemings", r"@FmrRepMTG", r"@realC_Collins", r"@SenMullin", r"@LisaBRochester", r"@RepChrisStewart", r"@KristiNoem", r"@DevinNunes", r"@RepLoisFrankel", 
                               r"@Grace4NY", r"@epaleezeldin", r"@RepDannyDavis", r"@SecFudge", r"@NikemaWilliams", r"@BobbyLRush", r"@RepGregStanton", r"@RepMcCaul", r"@RepMikeGarcia", r"@stephaniebice", r"@RepHoulahan", r"@RepZoeLofgren", r"@RepCardenas", r"@SenatorAndyKim", r"@SenatorBanks", r"@voteloucorrea", 
                               r"@CoopForCongress", r"@RepEdCase", r"@ElectFrench", r"@RepMcClintock", r"@tomemmer", r"@RepPaulTonko", r"@SecCardona", r"@RepMikeJohnson", r"@ElissaSlotkin", r"@RepPeteOlson", r"@laurenboebert", r"@RepGregMurphy", r"@RepByrne", r"@RepSusieLee", r"@ClyburnSC06", r"@LuetkemeyerB", 
                               r"@BradleyByrne", r"@MikeJohnson", r"@PatRyanUC", r"@RepTipton", r"@RepBonnie", r"@JakeAuch", r"@SpencerJCox", r"@andybiggs4az", r"@BarbaraLee_CA", r"@RepGregPence", r"@StaceyPlaskett", r"@IlhanMN", r"@CharlieCrist", r"@RepRiggleman", r"@GovNedLamont", r"@RepShimkus", r"@RealBenCarson", 
                               r"@DerekKilmer", r"@ShontelMBrown", r"@AndyBeshearKY", r"@TeamRoby", r"@RepRonWright", r"@CedricRichmond", r"@Armstrong_ND", r"@RepTedDeutch", r"@SecretaryAcosta", r"@MarkDeSaulnier", r"@RepLeeZeldin", r"@SaraJacobsCA", r"@RepKathleenRice", r"@MikeCareyOH15", r"@RepHagedorn", 
                               r"@GovMLG", r"@RepMoBrooks", r"@SecVetAffairs", r"@MichaelJCloud", r"@RepStefanik", r"@FrankPallone", r"@RepSires", r"@Jenniffer", r"@GerryConnolly", r"@Malinowski", r"@RepDonBacon", r"@krhern", r"@DavidValadao", r"@RepBenCline", r"@WarrenDavidson", r"@KimReynoldsIA", 
                               r"@RepDavidEPrice", r"@RepAshleyHinson", r"@RepGarretGraves", r"@jamie_raskin", r"@BillPoseyFL", r"@AyannaPressley", r"@RepSchrader", r"@EspaillatNY", r"@Bilirakis", r"@RepYvetteClarke", r"@NancyMace", r"@LoriTrahanMA", r"@SenatorRicketts", r"@JGO_2024", r"@ReoMarthaRoby", 
                               r"@MacTXPress", r"@RepJohnRose", r"@RepFrankLucas", r"@RepRickCrawford", r"@repdavidscott", r"@RepValDemings", r"@JoeNeguse", r"@RepAndyBarr", r"@USRepKeating", r"@RepKinzinger", r"@RepFredUpton", r"@RepSarbanes", r"@DCIARatcliffe", r"@RepMarkWalker", r"@RepBoebert", r"@RonnyJacksonTX", 
                               r"@RepFitzgerald", r"@CollinsFL19", r"@JaredHuffman", r"@JimPressOffice", r"@RepWilson", r"@RepTomGraves", r"@RepDebDingell", r"@RepBlakeMoore", r"@RepJoeWilson", r"@TeamKatiePorter", r"@RepJimCooper", r"@DebHaalandNM", r"@RepMikeQuigley", 
                               r"@DonaldNorcross", r"@BrianMastFL", r"@RepKatiePorter", r"@RepGuthrie", r"@MarthaRobyAL", r"@RepLoriTrahan", r"@CongressmanJVD", r"@ODNIgov", r"@RepRaskin", r"@RepSeanMaloney", r"@Call_Me_Dutch", r"@RepBice", r"@PeteAguilar", r"@xochnm", r"@BrianKempGA", r"@RepGrothman", 
                               r"@RepDelBene", r"@GovPhilScott", r"@RepClayHiggins", r"@ElaineLuria", r"@RepMrvan", r"@RepJimmyPanetta", r"@RepFrenchHill", r"@RepJoeCourtney", r"@RepKweisiMfume", r"@tatereeves", r"@sethmoulton", r"@CongressmanGT", r"@JimLangevin", r"@MadeleineDean", r"@justinamash", r"@RepRaulGrijalva", 
                               r"@GovernorGordon", r"@HurdOnTheHill", r"@FischbachMN7", r"@RepChuyGarcia", r"@RashidaTlaib", r"@RepMMM", r"@RepEspaillat", r"@cathymcmorris", r"@RepDevinNunes", r"@Abby4Iowa", r"@RepDwightEvans", r"@PeteRicketts", r"@RepSteveStivers", r"@XavierBecerra", r"@JeffFortenberry", 
                               r"@repmayraflores", r"@Troy_Balderson", r"@GovRonDeSantis", r"@Yvette4congress", r"@SecElaineChao", r"@reptimmons", r"@gusbilirakis", r"@RepRobinKelly", r"@BillPascrell", r"@RepMarieNewman", r"@jbletlow", r"@RepTomPrice", r"@RudyYakym", r"@GovernorTomWolf", r"@NedLamont", r"@RepDanBishop", 
                               r"@USRepKCastor", r"@RepEliotEngel", r"@RepAndreCarson", r"@GovHawaii", r"@TomTiffanyWI", r"@GovBillLee", r"@AngieCraigMN", r"@GovRaimondo", r"@repmarkpocan", r"@RepKahele", r"@repkevinhern", r"@RyanZinke", r"@timburchett", r"@RepDean", r"@MattRosendale", r"@katieporteroc", r"@econJaredB", 
                               r"@DarrenSoto", r"@RepSusanDavis", r"@RandyFeenstra", r"@EPAScottPruitt", r"@GovRauner", r"@Lancegooden", r"@RepKatCammack", r"@RepVanTaylor", r"@RepBobbyRush", r"@RepDavidRouzer", r"@RepKClark", r"@MaxRose4NY", r"@mlfudge", r"@GOPLeader", r"@GovernorPerry", r"@RepAngieCraig", 
                               r"@RepLoudermilk", r"@GReschenthaler", r"@PhilMurphy", r"@SupervisorCook", r"@claudiatenney", r"@SonnyPerdue", r"@virginiafoxx", r"@RoKhanna", r"@davidcicilline", r"@SpanbergerVA07", r"@RepMichaelCloud", r"@BobbyLRushMC", r"@RepMullin", r"@MondaireJones", r"@RepJimBaird", r"@Dr_RaulRuiz", 
                               r"@BennieGThompson", r"@Denver4VA", r"@SecretaryRoss", r"@RepMikeCarey", r"@JodyHiceGA", r"@RepRickAllen", r"@RepTomRice", r"@SusanWBrooks", r"@RepDanKildee", r"@MaElviraSalazar", r"@DrKimSchrier", r"@RepRichardNeal", r"@joekennedy", r"@RepUnderwood", r"@RepLloydDoggett", 
                               r"@RepJenniffer", r"@JoaquinCastrotx", r"@OAGMaryland", r"@JacksonLeeTX18", r"@Hurdonthehill", r"@RepLisaMcClain", r"@ericswalwell", r'@RepSwalwell', r"@balancingactx", r"@DebbieLesko", r"@ThomasMassie", r"@RepStephMurphy", r"@DWStweets", r"@WHCOS46", r"@RepRoybalAllard", r"@RepSeanDuffy", 
                               r"@NormaJTorres", r"@RepKManning", r"@SBAIsabel", r"@RepKenBuck", r"@TedBuddNC", r"@RepDrewFerguson", r"@ActSecJulieSu", r"@TXRandy14", r"@AliMayorkas", r"@HornForCongress", r"@davidschweikert", r"@RepThomasMassie", r"@SanfordBishop", r"@RepDianaDeGette", 
                               r"@Kilili_Sablan", r"@SteveKingIA", r"@repcleaver", r"@BobLighthizer", r"@RepTorresSmall", r"@deanbphillips", r"@AlLawsonJr", r"@RepBobGood", r"@DelgadoforNY", r"@RepVisclosky", r"@RepDarrenSoto", r"@kevinomccarthy", r"@Kat_Cammack", r"@mikepompeo", r"@GovDunleavy", r"@ChadFWolf", r"@DHS_Wolf", r"@RepAndyBiggsAZ", 
                               r"@USDOL", r"@CharlieBakerMA", r"@RepDeborahRoss", r"@Rigglema7Denver", r"@JoyceBeatty", r"@JBPritzker", r"@RepMikeRogersAL", r"@RepSpeier", r"@Murphy4OCMayor", r"@JohnBelEdwards", r"@JohnYarmuth", r"@RepSteveChabot", r"@RitchieTorres", r"@VickyHartzler", r"@JohnSarbanes", r"@hakeemjeffries", 
                               r"@JayObernolte", r"@DrPhilRoe", r"@SecYellen", r"@DustyJohnson", r"@RepDonaldPayne", r"@RepGwenMoore", r"@DunnCampaign", r"@DeGette5280", r"@ColinAllredTX", r"@kevinstitt", r"@GabeforColorado", r"@RepBuddyCarter", r"@WVGovernor", r"@PeteButtigieg", r"@SecretaryCarson", 
                               r"@HolcombForIN", r"@Josh4Jersey", r"@AdamSchiff", r"@realcawthorn", r"@RepTerriSewell", r"@JoshHarder", r"@CIADirector", r"@RepTroyNehls", r"@AustinScottGA08", r"@chuck4congress", r"@AmbassadorTai", r"@GovofCO", r"@chelliepingree", r"@DepSecXoch", r"@Tom_Suozzi", r"@Gwen4Congress", r"@RepJeffries", 
                               r"@RepGusBilirakis", r"@SecGranholm", r"@WhipKClark", r"@ElaineLuriaVA", r"@DavidShulkin", r"@GinaRaimondo", r"@stevebullockmt", r"@RepAndyHarrisMD", r"@StevenHorsford", r"@RepAdams", r"@RepMann", r"@RepBost", r"@RepKarenBass", r"@CIA", r"@BlaineACII", r"@GovKathyHochul", 
                               r"@JoeSempo", r"@RepPfluger", r"@POTUS45", r"@RepRatcliffe", r"@DepSecTodman", r"@GKButterfield", r"@LacyClayMO1", r"@DustyJohnsonSD", r"@GovJanetMills", r"@reptomemmer", r"@RepDavid", r"@DebDingell", r"@SteveStivers", r"@GovernorBullock", r"@RepHaleyStevens", r"@TeresaForNM", 
                               r"@USRepMikeFlood", r"@MikeFloodNE", r"@SpeakerPelosi", r"@SenAdamSchiff", r"@RepMichaelGuest", r"@janschakowsky", r"@AsaHutchinson", r"@KathyManningNC", r"@RepJerryNadler", r"@SpeakerJohnson", r"@LeeMZeldin", r"@SteveSisolak", r"@CMillerTIgerHwk", r"@SeanPMaloney", r"@RepGregSteube", r"@RepLaHood", 
                               r"@GovEvers", r"@RepCuellar", r"@PatrickMcHenry", r"@RepCarolMiller", r"@RepBobGibbs", r"@SecDef", r"@DebbieforFL", r"@WhipHoyer", r"@repdonyoung", r"@gretchenwhitmer", r"@RepWebster", r"@RepMcGovern", r"@RepBryanSteil", r"@RepBillFoster", r"@millermeeks", r"@RepJohnLarson", r"@RepJoseSerrano", 
                               r"@ConawayTX11", r"@ElissaSlotkin", r"@SenatorSlotkin", r"@RepYoungKim", r"@repgabeevans", r"@Chuy4Congress", r"@RepJimCosta", r"@RepLucyMcBath", r"@JasonSmithMO", r"@dankildee", r"@MayraFlores4TX", r"@WelchForVT", r"@TeamKClark", r"@AlbioSiresNJ", r"@DarinLaHoodIL", r"@EliseStefanik", r"@CarlosGimenezFL", 
                               r"@SecWilkie", r"@JackieSpeier", r"@RussVought45", r"@TedYoho", r"@JimmyGomezCA", r"@RepDavidValadao", r"@JakeEllzey", r"@USRepMikeDoyle", r"@Buddy_Carter", r"@bobbyrushfor1st", r"@RepHastingsFL", r"@RepBrianBabin", r"@RepRossSpano", r"@MarkwayneMullin", r"@RepFletcher", r"@RepArmstrongND", 
                               r"@SBAJovita", r"@RepSamGraves", r"@RepBrindisi", r"@RepWalorski", r"@BradSherman", r"@GovPritzker", r"@ByronDonalds", r"@dougducey", r"@RepMGS", r"@USAmbUN", r"@RepOHalleran", r"@RepJohnKatko", r"@RepBarragan", r"@TJCoxCongress", r"@stevenmnuchin1", r"@SecNielsen", r"@RepJeffDuncan", 
                               r"@KarenBassLA", r"@billhuizenga", r"@KatieHill4CA", r"@repblumenauer", r"@RepRWilliams", r"@mikeparson", r"@GavinNewsom", r"@DonJBacon", r"@gregsteube", r"@PramilaJayapal", r"@AndyKimNJ", r"@RepBeatty", r"@RepThompson", r"@RepFredKeller", r"@LaurenUnderwood", r"@BruceRaunerHQ", r"@Jeff_Rosen", r"@LoriTrahanMA", 
                               r"@MassieforKY", r"@rosadelauro", r"@AugustPfluger", r"@DennyHeck", r"@RepBlainePress", r"@RepLindaSanchez", r"@TomReedCongress", r"@RepMikeTurner", r"@collinpeterson", r"@RepDennyHeck", r"@AlmaforCongress", r"@RepCummings", r"@RepLouCorrea", r"@JamesComer", r"@RepGarbarino", r"@jasoninthehouse", 
                               r"@RepMarciaFudge", r"@GovMurphy", r"@LindaTSanchez", r"@RepBlaine", r"@SenTedBuddNC", r"@RepLarryBucshon", r"@econjared", r"@Rep_Peltola", r"@CongressmanRaja", r"@jlmmattis", r"@KathyHochul", r"@SecAzar", r"@SecBrouillette", r"@HarleyRouda", r"@Rep_Watkins", r"@BHigginsBflo", 
                               r"@JulieSuLabor", r"@Robert_Aderholt", r"@JakeLaTurner", r"@RepPeteStauber", r"@RepLipinski", r"@RonDeSantis", r"@HoulahanForPa", r"@RepAdamSmith", r"@RepJahanaHayes", r"@ScottPruittOK", r"@GregAbbott_TX", r"@RepSchneider", r"@ShalandaYoung46", r"@davidjtrone", r"@MelanieforNM", r"@rep_stevewomack", 
                               r"@RepCloudTX", r"@RepKirkpatrick", r"@RepAlGreen", r"@GovernorKayIvey", r"@RepAbraham", r"@RepRobWoodall", r"@CongressmanHice", r"@LouisianaGov", r"@RepBowman", r"@tedlieu", r"@TeamPelosi", r"@LarryHogan", r"@StenyHoyer", r"@DrPaulGosar", r"@RepSusanWild", r"@SenLBR", r"@Ann_Kirkpatrick", 
                               r"@danbishopnc", r"@RepSmucker", r"@RepTimRyan", r"@RepKimSchrier", r"@Donald_McEachin", r"@RepGonzalez", r"@Cline4Virginia", r"@VoteMeijer", r"@SecPriceMD", r"@HaleyforMI", r"@SeanCasten", r"@RepHolding", r"@MarioDB", r"@NikkiHaley", r"@michaelgwaltz", r"@RepBillFlores", r"@RepTrey", 
                               r"@RoyCooperNC", r"@SecDuffy", r"@EPAMichaelRegan", r"@RepHarshbarger", r"@lucymcbath", r"@DesJarlaisTN04", r"@RepBRochester", r"@MattForMontana", r"@MarkAmodeiNV2", r"@Reince", r"@RepPaulCook"]

twitter_handles_senators = [r'@senatemajldr',r"@amyklobuchar", r"@ChrisCoons", r"@hoeven4senate", r"@SenGillibrand", r"@SenSchumer", r"@MarkWarner", r"@SenatorWicker", r"@SenJohnBarrasso", r"@DickDurbin", r"@SenPatRoberts", 
                            r"@SenatorTimScott", r"@tedcruz", r"@ChuckGrassley", r"@CynthiaMLummis", r"@SenThomTillis", r"@RoyBluntMO", r"@WydenPress", r"@SenCortezMasto", r"@SenAngusKing", r"@TinaSmithMN", 
                            r"@SenatorDurbin", r"@CoachForGov", r"@SenTimKaine", r"@SenToomey", r"@SenHawleyPress", r"@ewarren", r"@RogerMarshallMD", r"@LeaderJohnThune", r"@SenatorFischer", r"@JohnCornyn", 
                            r"@HawleyMO", r"@MartinHeinrich", r"@RandPaul", r"@MichaelBennet", r"@SecRubio", r"@GaryPeters", r"@RonWyden", r"@SenDanSullivan", r"@RosenforNevada", r"@SenWhitehouse", 
                            r"@SenJeffMerkley", r"@SenCoryGardner", r"@ReverendWarnock", r"@MittRomney", r"@SenatorCardin", r"@ThomTillis", r"@sendavidperdue", r"@PattyMurray", r"@SenatorRomney", 
                            r"@KLoeffler", r"@maziehirono", r"@ChrisVanHollen", r"@tammybaldwin", r"@SenShelby", r"@BobMenendezNJ", r"@DickBlumenthal", r"@chuckschumer", r"@ScottforFlorida", 
                            r"@TammyDuckworth", r"@Hickenlooper", r"@AlexPadilla4CA", r"@BenSasse", r"@TomCottonAR", r"@SenBobCasey", r"@CaptMarkKelly", r"@MurrayCampaign", r"@SenJackReed", r"@timkaine", 
                            r"@SenatorShaheen", r"@SenatorCarper", r"@GrassleyPress", r"@RonJohnsonWI", r"@ossoff", r"@SenGaryPeters", r"@CapitoforWV", r"@SenJoniErnst", r"@DougJones", r"@brianschatz", 
                            r"@lisamurkowski", r"@SenWarren", r"@SenatorRisch", r"@SenBillCassidy", r"@votetimscott", r"@SenTedCruz", r"@SenRandPaul", r"@Boozman4AR", r"@SenatorLoeffler", r"@SenDuckworth", 
                            r"@braun4indiana", r"@SenMikeLee", r"@kyrstensinema", r"@SenatorRounds", r"@SenMcConnell", r"@CoryBooker", r"@VoteMarsha", r"@SenTinaSmith", r"@LindseyGrahamSC", r"@BillHagertyTN", 
                            r"@SenAlexPadilla", r"@SenCapito", r"@ToddYoungIN", r"@SenHydeSmith", r"@SenatorLujan", r"@SenatorCantwell", r"@SenStabenow", r"@McConnellPress", r"@SenSanders", r"@MarshaBlackburn", 
                            r"@robportman", r"@SenatorBennet", r"@gillibrandny", r"@SenJackyRosen", r"@SenFeinstein", r"@SenRonJohnson", r"@SenatorBurr", r"@JimInhofe", r"@Sen_JoeManchin", r"@SenJohnHoeven", 
                            r"@SenatorHeinrich", r"@MikeCrapo", r"@SenMarkey", r"@JerryMoran", r"@SenatorTomUdall", r"@marcorubio", r"@SenatorHassan", r"@SenMarkKelly", r"@SenatorCollins", r"@SenTuberville", 
                            r"@SenRickScott", r"@kevincramer", r"@SenatorLeahy", r"@SenBooker", r"@SenatorWarner", r"@GovBraun", r"@SenDougJones", r"@Maggie_Hassan", r"@SenBrianSchatz", r"@SenToddYoung", 
                            r"@SenJohnKennedy", r"@JohnBoozman", r"@SenatorWarnock", r"@ChrisMurphyCT", r"@EdMarkey", r"@SenKevinCramer", r"@SenCoonsOffice", r"@SenatorEnzi", r"@SenAmyKlobuchar", 
                            r"@SteveDaines", r"@SenatorMenendez", r"@SenatorLankford", r"@BillCassidy", r"@InhofePress", r"@PatToomey", r"@SenTomCotton", r"@johnthune", r"@SenatorBaldwin", r"@RoyBlunt", 
                            r"@SenBlumenthal", r"@CoryGardner", r"@joniernst", r"@benraylujan", r"@BernieSanders", r"@SenSherrodBrown", r"@SenAlexander", r"@SenatorTester", r"@RepAnnieKuster", r"@RepMarkPocan", 
                            r"@RepRonnyJackson", r"@RepDanCrenshaw", r"@RepJoshHarder", r"@RepAOC", r"@LisaMurkowski", r"@RussFulcher", r"@RepColinAllred", r"@RepGaramendi", r"@JohnThune", r"@RepMayraFlores", 
                            r"@RepTimBurchett", r"@RepSaraJacobs", r"@RepDelgado", r"@RepBillyLong", r"@KweisiMfume", r"@RepMikeBost", r"@JamesLankford", r"@SenSasse", r"@RepMaryPeltola", r"@RepJimMcDermott", 
                            r"@RepKatieHill", r"@RepGraceMeng", r"@SenOssoff", r"@VirginiaFoxx", r"@GregWalden", r"@KathleenRice", r"@RepDonYoung", r"@RepDWStweets", r"@RepStephenLynch", r"@RepLizCheney", 
                            r"@Ilhan", r"@RobPortman", r"@TedCruz", r"@RepJamesComer", r"@RepMaloney", r"@RepNikema", r"@RepDebHaaland", r"@RepMondaire", r"@RepRussFulcher", r"@RepBrianMast", r"@RepJasonSmith", 
                            r"@RepChipRoy", r"@RepBethVanDuyne", r"@RepTedLieu", r"@ConorLambPA", r"@LamarAlexander", r"@FrankDLucas", r"@MacThornberry", r"@RepRashida", r"@RepMcKinley", r"@GregMurphyMD", 
                            r"@GeorgeHolding", r"@RepDarrellIssa", r"@GarretGraves", r"@RepJimmyGomez", r"@RepBurgessOwens", r"@RepDinaTitus", r"@RepLouieGohmert", r"@RepNancyMace", r"@RepRoKhanna", r"@RepTedYoho", 
                            r"@RepMariaSalazar", r"@AmyKlobuchar", r"@RepSylviaGarcia", r"@MazieHirono", r"@RepDavidKustoff", r"@KwanzaHall", r"@RepKevinHern", r"@RepRobBishop"]

twitter_handles_institutions = [r'@PressSec', r'@StateDept', r"@NWDUSACE", r"@medicarepayment", r"@Southcom", r"@USACEGALVESTON", r"@NatLabRockies", r"@NLM_NIH", r"@voakorea", r"@USACEHQ", r"@Research_USDOT", r"@USDOL", r"@SecWar", r"@VozdeAmerica", r"@USAGM", r"@WHOMB", r"@USPBGC", r"@federallabs", r"@USIP", r"@usagmceo", r"@ILAB_DOL", r"@bts_usdot", 
                           r"@InvasiveInfo", r"@WHCEQ46", r"@NIC_DOJ", r"@CEA47", r"@BOEM", r"@WhiteHouse", r"@ACFHHS", r"@CPECBRND", r"@VOAfarsi", r"@Livermore_Lab", r"@librarycongress", r"@NIH_NINDS", r"@NOAAFisheries", r"@AbilityOneProg", r"@NIH", r"@ciodotgov", r"@USACEBaltimore", r"@MVD_USACE", r"@federalreserve", r"@usdaRD", 
                           r"@FMCS_USA", r"@ArcticResearch", r"@HouseDailyPress", r"@VOAThai", r"@RepDebHaaland", r"@AtlantaCorps", r"@tsp4gov", r"@eeregov", r"@OJPOJJDP", r"@NCDgov", r"@NBRC_Team", r"@CFPB", r"@NIH_NIDCD", r"@ASKNCELA1", r"@ArmyCorpsNAD", r"@GolosAmeriki", r"@DLAMIL", r"@HouseDemocrats", r"@SecRollins", 
                           r"@DOIONRR", r"@OCS_ACFgov", r"@usiporgold", r"@UnderSecT", r"@BEPgov", r"@martinoticias", r"@DeptofDefense", r"@CivilRights", r"@NTISInfo", r"@NIH_NHLBI", r"@USAfricaCommand", r"@WesternAreaPowr", r"@USADF", r"@National_Ag_Lib", r'@CDCgov', r"@CDCEnvironment", r"@NationalParkFdn", r"@USACELRD", r"@ENERGY", 
                           r"@Ilhan", r"@VOATurkce", r"@NLRB", r"@USAFReserve", r"@VOAAfrique", r"@SecDebHaaland", r"@DCMAnews", r"@HouseGOP", r"@ED_Sped_Rehab", r"@VaVeteransSvcs", r"@USCIS", r"@INDOPACOM", r"@ArmySMDC", r"@TheUSSCgov", r"@OWprogram", r"@USOPM", r"@OCWR_LegBranch", r"@AHRQGov", r"@NWS", r"@DHSgov", r"@FJC_Research", r"@NIMHDirector"]

twitter_handles_committees = [r"@NatResources", r"@WaysandMeansGOP", r"@HouseAgGOP", r"@EnergyDems", r"@JudiciaryGOP", r"@FSCDems", r"@SenateBudget", r"@sciencedems", r"@WaysMeansCmte", r"@HouseForeignGOP", r"@SenateSmallBiz", r"@HouseAdm_Dems", r"@GOPoversight", r"@HouseSmallBiz", r"@HASCDemocrats", r"@SVACGOP", r"@HouseCommerce", 
                              r"@TransportDems", r"@SenateCommerce", r"@NRDems", r"@HSBCDems", r"@SenateAging", r"@IndianCommittee", r"@SenJudiciaryGOP", r"@HouseForeign", r"@TransportGOP", r"@HSGAC_GOP", r"@jctgov", r"@HASCRepublicans", r"@SenateApprops", r"@EPWCmte", r"@JECDems", r"@SenateBanking", r"@SVACDems", r"@EnergyCommerce", 
                              r"@OversightDems", r"@SenateFinance", r"@HouseVetAffairs", r"@JCCIC", r"@HouseAgDems", r"@SenFinance", r"@EnergyGOP", r"@housebudgetGOP", r"@SASCGOP", r"@EdWorkforceCmte", r"@SenateAgDems", r"@SFRCdems", r"@FinancialCmte", r"@HomelandGOP", r"@HouseAdmin", r"@HouseBudgetDems", r"@RulesDemocrats", 
                              r"@RulesReps", r"@committeeonccp", r"@HouseIntelDems", r"@SASCDems", r"@VetAffairsDems", r"@JudiciaryDems", r"@SenateForeign", r"@SenateAgingDems", r"@SenateRules", r"@EdWorkforceDems", r"@HouseAppropsGOP", r"@HELPCmteDems", r"@GOPHELP", r"@HouseJudiciary", r"@AppropsDems", r"@HouseScience", 
                              r"@BudgetGOP", r"@HouseIntel", r"@JECRepublicans", r"@EPWGOP", r"@HomelandDems"]

twitter_handles_other_politicians = [r"@Dr_AnthonyFauci", r"@DirectorWray", r"@WilliamPBarr"]

# State-level filter
states = [r"local", r"Alabama", r"Alaska", r"Arizona", r"Arkansas", r"American Samoa", r"California", r"Colorado", r"Connecticut", r"Delaware", r"District of Columbia", 
         r"Florida", r"Georgia", r"Guam", r"Hawaii", r"Idaho", r"Illinois", r"Indiana", r"Iowa", r"Kansas", r"Kentucky", r"Louisiana", r"Maine", r"Maryland", r"Massachusetts", 
         r"Michigan", r"Minnesota", r"Mississippi", r"Missouri", r"Montana", r"Nebraska", r"Nevada", r"New Hampshire", r"New Jersey", r"New Mexico", r"New York", r"North Carolina", 
         r"North Dakota", r"Northern Mariana Islands", r"Ohio", r"Oklahoma", r"Oregon", r"Pennsylvania", r"Puerto Rico", r"Rhode Island", r"South Carolina", r"South Dakota", 
         r"Tennessee", r"Texas", r"Trust Territories", r"Utah", r"Vermont", r"Virginia", r"Virgin Islands", r"Washington", r"West Virginia", r"Wisconsin", r"Wyoming", r"US", 
         r"AL", r"AK", r"AZ", r"AR", r"AS", r"CA", r"CO", r"CT", r"DE", r"DC", r"FL", r"GA", r"GU", r"HI", r"ID", r"IL", r"IN", r"IA", r"KS", r"KY", r"LA", r"ME", r"MD", 
         r"MA", r"MI", r"MN", r"MS", r"MO", r"MT", r"NE", r"NV", r"NH", r"NJ", r"NM", r"NY", r"NC", r"ND", r"MP", r"OH", r"OK", r"OR", r"PA", r"PR", r"RI", r"SC", r"SD", r"TN", 
         r"TX", r"TT", r"UT", r"VT", r"VA", r"VI", r"WA", r"WV", r"WI", r"WY"]

# Extra Filter for supreme judges (to make sure it refers to the correct persons). 
# For all other names list I use the condition that at least 1 more matched term needs to be included. This ensures that the correct persons are selected.
extra_filter_supreme = [r"Judge", r"J\.", r"Justice", r"Court", r"Supreme"]

# Filter: Ensure that US_institutions only refers to federal-level institutions
federal_institutions_only = [
    inst for inst in US_institutions
    if inst not in potential_state_institutions
]

_states_pattern = r'(?:' + '|'.join(map(regex.escape, states)) + r')'
no_state_lookbehind = rf'(?<!(?:\b{_states_pattern})\s)'
no_state_lookahead  = rf'(?!\s+in\s+(?:{_states_pattern}\b))'

# Wrap institutions in filters
checked_potential_state_institutions = [no_state_lookbehind + '(?:' + inst + ')' + no_state_lookahead for inst in potential_state_institutions]
checked_US_institutions = checked_potential_state_institutions + federal_institutions_only
checked_senate = no_state_lookbehind + '(?:' + senate + ')' + no_state_lookahead

# Compile into regex pattern: search strings
committees_regex = regex.compile('|'.join(committees), regex.IGNORECASE)
congress_regex = re.compile('|'.join(congress_members), re.IGNORECASE)
cabinet_regex = re.compile('|'.join(cabinet_members), re.IGNORECASE)
governors_regex = re.compile('|'.join(governors), re.IGNORECASE)
senators_regex = re.compile('|'.join(senators), re.IGNORECASE)
justices_regex = re.compile('|'.join(supreme_justices), re.IGNORECASE)
other_politicians_regex = re.compile('|'.join(other_politicians), re.IGNORECASE)

unambiguous_politicians_regex = re.compile('|'.join(unambiguous_politicians), re.IGNORECASE)
aliases_politicians_regex = re.compile('|'.join(aliases_politicians), re.IGNORECASE)
surnames_only_regex = regex.compile(rf"(?:(?i:{'|'.join(surnames_only)})|{'|'.join(aliases_short)})")
title_combo_regex = re.compile("|".join(title_combos), re.IGNORECASE)
abbreviations_regex = re.compile('|'.join(abbreviations))

# Create lists of senator/governor/congress(wo)man + name combinations: either surname or first name AND surname
def title_surname_patterns(title_variants, names):
    patterns = []
    for name in names:
        parts = name.split()
        for start in range(len(parts)):
            suffix = r'\s+'.join(regex.escape(p) for p in parts[start:])
            for title in title_variants:
                patterns.append(rf'(?<![A-Za-z0-9]){title}\s+{suffix}(?![A-Za-z0-9])')
    return patterns

senator_title    = [r'(?:sen(?:ator)?\.?)']
governor_title   = [r'(?:gov(?:ernor)?\.?)']
legislator_title = [r'(?:rep(?:resentative)?\.?)', r'congressman', r'congresswoman']
justice_title    = [r'(?:j(?:ustice)?\.?)']

senator_surnames    = title_surname_patterns(senator_title, senators)
governor_surnames   = title_surname_patterns(governor_title, governors)
legislator_surnames = title_surname_patterns(legislator_title, congress_members)
justice_surnames    = title_surname_patterns(justice_title, supreme_justices)

# title + handle combinations
def title_handle_patterns(title_variants, handle_list):
    patterns = []
    for handle in handle_list:
        escaped = regex.escape(handle)
        for title in title_variants:
            patterns.append(rf'(?<![A-Za-z0-9]){title}\s+{escaped}')
    return patterns

senator_title_handle_combo = title_handle_patterns(senator_title,
                                        twitter_handles_senators)
governor_title_handle_combo = title_handle_patterns(governor_title,
                                        twitter_handles_politicians)
legislator_title_handle_combo = title_handle_patterns(legislator_title,
                                        twitter_handles_politicians)

# Compile into regex
senator_surname_regex = re.compile('|'.join(senator_surnames), re.IGNORECASE)
governor_surname_regex = re.compile('|'.join(governor_surnames), re.IGNORECASE)
legislator_surname_regex = re.compile('|'.join(legislator_surnames), re.IGNORECASE)
justice_surname_regex = re.compile('|'.join(justice_surnames), re.IGNORECASE)

# Compile into regex: title + handle combinations
senator_title_handle_combo_regex     = re.compile('|'.join(senator_title_handle_combo),     re.IGNORECASE)
governor_title_handle_combo_regex = re.compile('|'.join(governor_title_handle_combo), re.IGNORECASE)
legislator_title_handle_combo_regex = re.compile('|'.join(legislator_title_handle_combo), re.IGNORECASE)


# Cheap pre-screen: only run title+handle step when a title keyword is present
prescreen_committees = regex.compile(
    r'(?<![A-Za-z0-9])Committee',
    regex.IGNORECASE
)
prescreen_senator = regex.compile(
    r'(?<![A-Za-z0-9])Sen(?:ator\b|\.)?(?![A-Za-z0-9])',
    regex.IGNORECASE
)
prescreen_governor = regex.compile(
    r'(?<![A-Za-z0-9])Gov(?:ernor\b|\.)?(?![A-Za-z0-9])',
    regex.IGNORECASE
)
prescreen_congress = regex.compile(
    r'(?<![A-Za-z0-9])(?:Rep(?:resentative\b|\.\b)?|Congressman|Congresswoman|Congressmember\b)(?![A-Za-z0-9])',
    regex.IGNORECASE
)

# Compile into regex: rest
filter_justices_regex = re.compile('|'.join(extra_filter_supreme), re.IGNORECASE)
senator_regex = regex.compile(senator, regex.IGNORECASE)
governor_regex = regex.compile(governor, regex.IGNORECASE)
legislator_regex = regex.compile('|'.join(legislator), regex.IGNORECASE)
senate_regex = regex.compile(checked_senate, regex.IGNORECASE)

# Compile into regex: twitter handles
politicians_handles_regex = re.compile('|'.join(twitter_handles_politicians), re.IGNORECASE)
senators_handles_regex = re.compile('|'.join(twitter_handles_senators), re.IGNORECASE)
institutions_handles_regex = re.compile('|'.join(twitter_handles_institutions), re.IGNORECASE)
committees_handles_regex = re.compile('|'.join(twitter_handles_committees), re.IGNORECASE)
combo_handles_regex = re.compile('|'.join(combo_handles), re.IGNORECASE)
other_politicians_handles_regex = re.compile('|'.join(twitter_handles_other_politicians), re.IGNORECASE)

# Combined lists (computationally more efficient: checks lists only once)
combo_check_required = regex.compile(
        '(?:'
        + '|'.join('(?i:%s)' % p for p in (
                checked_US_institutions +
                combo_handles +
                unambiguous_politicians))
        + '|'
        + '|'.join('(?:%s)' % p for p in abbreviations)
        + ')'
    )

standalone_matches = regex.compile(
    '|'.join([
        '(?:' + p + ')' for p in (
            twitter_handles_politicians +
            twitter_handles_senators +
            twitter_handles_institutions +
            twitter_handles_committees +
            twitter_handles_other_politicians +
            committees +
            aliases_politicians + 
            justice_surnames
        )
    ]),
    regex.IGNORECASE
)

one_additional_match = re.compile(
    '|'.join([
        '(?:' + p + ')' for p in (
            senators +
            congress_members +
            cabinet_members +
            governors +
            other_politicians
        )
    ]),
    re.IGNORECASE
)

# -----------------------------------------------------------------------------
# Extraction helpers and loop
# -----------------------------------------------------------------------------
def findall_terms(pattern, text):
    """Full match strings from findall. If the pattern has capturing groups,
    findall returns subgroup(s) or tuples — use finditer for the full match."""
    if pattern.groups:
        return [m.group(0) for m in pattern.finditer(text)]
    return pattern.findall(text)


def spans_overlap(s, e, spans):
    """True if [s, e) overlaps any span. Spans must be sorted by start."""
    for ss, ee in spans:
        if ss >= e:
            return False
        if s < ee and e > ss:
            return True
    return False


def add_span(spans, span):
    """Append span and keep spans sorted by start for fast overlap checks."""
    s, e = span
    lo, hi = 0, len(spans)
    while lo < hi:
        mid = (lo + hi) // 2
        if spans[mid][0] < s:
            lo = mid + 1
        else:
            hi = mid
    spans.insert(lo, (s, e))


def note_matched_term(term, matched_terms, seen, multi_word_lowers):
    """Record a unique matched term and track multi-word strings for dedup."""
    low = term.lower()
    if low in seen:
        return False
    seen.add(low)
    matched_terms.append(term)
    if ' ' in term:
        multi_word_lowers.append(low)
    return True


def subsumed_by_multi_word(low, multi_word_lowers):
    """True if low appears inside a previously matched multi-word phrase."""
    for mw in multi_word_lowers:
        if low in mw:
            return True
    return False


def extract_matched_terms(text):
    """Run steps 1–11; return matched_terms list (may be empty)."""
    matched_terms = []
    seen = set()
    spans = []
    multi_word_lowers = []

    for m in title_combo_regex.finditer(text):
        term = m.group()
        low = term.lower()
        if low not in seen:
            seen.add(low)
            matched_terms.append(term)
            add_span(spans, m.span())
            if ' ' in term:
                multi_word_lowers.append(low)

    for m in combo_check_required.finditer(text):
        s, e = m.span()
        if spans_overlap(s, e, spans):
            continue
        if note_matched_term(m.group(), matched_terms, seen, multi_word_lowers):
            add_span(spans, (s, e))

    if filter_justices_regex.search(text):
        for term in justices_regex.findall(text):
            note_matched_term(term, matched_terms, seen, multi_word_lowers)

    if prescreen_committees.search(text):
        matches = findall_terms(committees_regex, text)
        committee_found = bool(matches)
        for term in matches:
            note_matched_term(term, matched_terms, seen, multi_word_lowers)
        if not committee_found:
            note_matched_term('committee', matched_terms, seen, multi_word_lowers)

    for m in senate_regex.finditer(text):
        s, e = m.span()
        if committees_regex.match(text, s):
            continue
        note_matched_term(m.group(), matched_terms, seen, multi_word_lowers)

    if prescreen_senator.search(text):
        matches = (
            findall_terms(senator_surname_regex, text)
            + findall_terms(senator_title_handle_combo_regex, text)
        )
        senator_title_combo_found = bool(matches)
        for term in matches:
            note_matched_term(term, matched_terms, seen, multi_word_lowers)
        if not senator_title_combo_found:
            note_matched_term('senator', matched_terms, seen, multi_word_lowers)

    if prescreen_governor.search(text):
        matches = (
            findall_terms(governor_surname_regex, text)
            + findall_terms(governor_title_handle_combo_regex, text)
        )
        governor_title_combo_found = bool(matches)
        for term in matches:
            note_matched_term(term, matched_terms, seen, multi_word_lowers)
        if not governor_title_combo_found:
            low = 'governor'
            if low in text.lower() and low not in seen:
                note_matched_term(low, matched_terms, seen, multi_word_lowers)

    if prescreen_congress.search(text):
        matches = (
            findall_terms(legislator_surname_regex, text)
            + findall_terms(legislator_title_handle_combo_regex, text)
        )
        legislator_title_combo_found = bool(matches)
        for term in matches:
            note_matched_term(term, matched_terms, seen, multi_word_lowers)
        if not legislator_title_combo_found:
            text_lower = text.lower()
            for term in ('congressman', 'congresswoman', 'congressmember'):
                if term in text_lower and term not in seen:
                    note_matched_term(term, matched_terms, seen, multi_word_lowers)

    for term in findall_terms(standalone_matches, text):
        low = term.lower()
        if low in seen:
            continue
        if subsumed_by_multi_word(low, multi_word_lowers):
            continue
        note_matched_term(term, matched_terms, seen, multi_word_lowers)

    for m in surnames_only_regex.finditer(text):
        term = m.group()
        low = term.lower()
        if low in seen:
            continue
        if subsumed_by_multi_word(low, multi_word_lowers):
            continue
        note_matched_term(term, matched_terms, seen, multi_word_lowers)

    candidates = []
    candidates_seen = set()
    for term in one_additional_match.findall(text):
        low = term.lower()
        if low in seen or low in candidates_seen:
            continue
        if subsumed_by_multi_word(low, multi_word_lowers):
            continue
        candidates_seen.add(low)
        candidates.append(term)

    if matched_terms or len(candidates) >= 2:
        for term in candidates:
            note_matched_term(term, matched_terms, seen, multi_word_lowers)

    return matched_terms


def log_progress(processed, written, skipped, start_time, checkpoint):
    now = time.time()
    elapsed = now - start_time
    rate_avg = processed / elapsed if elapsed > 0 else 0

    parts = [
        f'Processed {processed:,} lines',
        f'written {written:,}',
        f'skipped {skipped:,}',
        f'{rate_avg:,.0f} lines/s avg',
    ]

    if checkpoint['time'] is not None:
        dt = now - checkpoint['time']
        dp = processed - checkpoint['processed']
        dw = written - checkpoint['written']
        if dt > 0 and dp > 0:
            window_rate = dp / dt
            window_match = dw / dp
            parts.append(f'{window_rate:,.0f} lines/s window')
            parts.append(f'{window_match:.1%} match window')

    parts.append(f'{elapsed:.1f}s elapsed')
    print(' | '.join(parts), flush=True)

    checkpoint['time'] = now
    checkpoint['processed'] = processed
    checkpoint['written'] = written


if __name__ == '__main__':
    start_time = time.time()
    processed = 0
    written = 0
    skipped = 0
    progress_checkpoint = {'time': None, 'processed': 0, 'written': 0}

    print(f'Reading {input_file} -> {output_file}', flush=True)

    with open(input_file, 'r', encoding='utf-8', errors='replace') as infile, \
         open(output_file, 'w', encoding='utf-8', buffering=OUTFILE_BUFFER_BYTES) as outfile:

        for line in infile:
            processed += 1
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                skipped += 1
                if processed % PROGRESS_EVERY == 0:
                    log_progress(processed, written, skipped, start_time, progress_checkpoint)
                continue

            if 'text' not in data:
                skipped += 1
                if processed % PROGRESS_EVERY == 0:
                    log_progress(processed, written, skipped, start_time, progress_checkpoint)
                continue

            matched_terms = extract_matched_terms(data['text'])

            if matched_terms:
                out_obj = {
                    'id': data['id'],
                    'text': data['text'],
                    'lang': data['lang'],
                    'author_id': data['author_id'],
                    'created_at': data['created_at'],
                    'public_metrics': data['public_metrics'],
                    'referenced_tweets': data['referenced_tweets'],
                    'matched_terms': matched_terms,
                }
                outfile.write(_dumps_obj(out_obj) + '\n')
                written += 1

            if processed % PROGRESS_EVERY == 0:
                log_progress(processed, written, skipped, start_time, progress_checkpoint)

    log_progress(processed, written, skipped, start_time, progress_checkpoint)
    print(f'Done. Output written to {output_file}', flush=True)