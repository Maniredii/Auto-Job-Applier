

from modules.helpers import make_directories
from config.settings import (run_in_background, stealth_mode, disable_extensions, safe_mode,
                            file_name, failed_file_name, logs_folder_path, generated_resume_path,
                            use_proxy, proxy_server, enable_human_behavior, randomize_timing,
                            enable_break_simulation)
from config.questions import default_resume_path
if stealth_mode:
    import undetected_chromedriver as uc
else:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    # from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from modules.helpers import find_default_profile_directory, critical_error_log, print_lg
from modules.stealth_engine import StealthEngine
from modules.stealth_login import perform_stealth_linkedin_login
from modules.human_behavior import HumanBehaviorSimulator
from modules.smart_application_strategy import SmartApplicationStrategy

try:
    make_directories([file_name,failed_file_name,logs_folder_path+"/screenshots",default_resume_path,generated_resume_path+"/temp"])

    # Initialize stealth engine
    stealth_engine = StealthEngine()

    print_lg("IF YOU HAVE MORE THAN 10 TABS OPENED, PLEASE CLOSE OR BOOKMARK THEM! Or it's highly likely that application will just open browser and not do anything!")

    # Determine profile directory
    profile_dir = None
    if safe_mode:
        print_lg("SAFE MODE: Will login with a guest profile, browsing history will not be saved in the browser!")
    else:
        profile_dir = find_default_profile_directory()
        if not profile_dir:
            print_lg("Default profile directory not found. Logging in with a guest profile, Web history will not be saved!")

    # Set up WebDriver with enhanced stealth options
    if stealth_mode:
        print_lg("🔒 Initializing ENHANCED stealth mode with advanced bot detection bypass...")

        try:
            # Configure proxy if enabled
            proxy = proxy_server if use_proxy and proxy_server else None
            options = stealth_engine.get_enhanced_chrome_options(profile_dir, proxy)

            if run_in_background:
                options.add_argument("--headless")
                print_lg("Running in headless mode")
            if disable_extensions:
                options.add_argument("--disable-extensions")
                print_lg("Extensions disabled")

            print_lg("Setting up stealth driver... This may take some time.")
            driver = stealth_engine.setup_stealth_driver(options)

            # Perform initial stealth checks
            stealth_engine.evade_detection_check(driver)

        except Exception as e:
            print_lg(f"❌ Stealth mode failed: {e}")
            print_lg("🛡️ Falling back to standard Chrome driver...")
            stealth_mode = False  # Fallback to standard mode

    else:
        print_lg("Using standard Chrome driver (stealth mode disabled)")
        options = Options()
        if run_in_background:   options.add_argument("--headless")
        if disable_extensions:  options.add_argument("--disable-extensions")
        if profile_dir: options.add_argument(f"--user-data-dir={profile_dir}")

        driver = webdriver.Chrome(options=options)
        driver.maximize_window()

    wait = WebDriverWait(driver, 10)  # Increased timeout for better reliability
    actions = ActionChains(driver)

    # Store enhanced modules for use in other parts of the application
    driver.stealth_engine = stealth_engine if stealth_mode else None

    # Initialize human behavior simulator if enabled
    if enable_human_behavior:
        driver.human_behavior = HumanBehaviorSimulator()
        print_lg("🤖 Human behavior simulation enabled")
    else:
        driver.human_behavior = None

    # Initialize smart application strategy
    driver.application_strategy = SmartApplicationStrategy()
    print_lg("🧠 Smart application strategy initialized")

    # Perform stealth LinkedIn login
    print_lg("🔐 Attempting stealth LinkedIn login...")
    login_success = perform_stealth_linkedin_login(driver, username, password)

    if login_success:
        print_lg("✅ Stealth login successful - bot undetected!")
    else:
        print_lg("⚠️ Stealth login had issues - manual intervention may be required")
except Exception as e:
    msg = 'Seems like either... \n\n1. Chrome is already running. \nA. Close all Chrome windows and try again. \n\n2. Google Chrome or Chromedriver is out dated. \nA. Update browser and Chromedriver (You can run "windows-setup.bat" in /setup folder for Windows PC to update Chromedriver)! \n\n3. If error occurred when using "stealth_mode", try reinstalling undetected-chromedriver. \nA. Open a terminal and use commands "pip uninstall undetected-chromedriver" and "pip install undetected-chromedriver". \n\n\nIf issue persists, try Safe Mode. Set, safe_mode = True in config.py \n\nPlease check GitHub discussions/support for solutions https://github.com/GodsScion/Auto_job_applier_linkedIn \n                                   OR \nReach out in discord ( https://discord.gg/fFp7uUzWCY )'
    if isinstance(e,TimeoutError): msg = "Couldn't download Chrome-driver. Set stealth_mode = False in config!"
    print_lg(msg)
    critical_error_log("In Opening Chrome", e)
    from pyautogui import alert
    alert(msg, "Error in opening chrome")
    try: driver.quit()
    except NameError: exit()
    
