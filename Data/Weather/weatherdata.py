from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import csv
import time
import os
import random
import sys
import argparse

def scrape_date_range(start_date, end_date, resume_from=None, force_rescrape=False):
    """
    Scrape temperature data for a range of dates
    
    Args:
        start_date: The first date to scrape
        end_date: The last date to scrape
        resume_from: If provided, start scraping from this date instead of start_date
        force_rescrape: If True, re-scrape dates even if they appear in the progress file
    """
    # Create a CSV file for all dates
    csv_filename = f'dallas_temps_{start_date.strftime("%Y%m%d")}_to_{end_date.strftime("%Y%m%d")}_complete.csv'
    
    # Check if we're resuming and the file exists
    file_exists = os.path.isfile(csv_filename)
    mode = 'a' if (file_exists and resume_from) else 'w'
    
    with open(csv_filename, mode, newline='') as csvfile:
        fieldnames = ['Date', 'Time', 'Temperature_F']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header only if creating a new file
        if mode == 'w':
            writer.writeheader()
        
        # Determine which date to start from
        current_date = resume_from if resume_from else start_date
        
        # Check if we're trying to scrape future dates
        today = datetime.now()
        if end_date > today:
            print(f"Warning: End date {end_date.strftime('%Y-%m-%d')} is in the future.")
            print(f"Data for future dates may be forecasts or unavailable.")
        
        # Create a progress file to track completed dates
        progress_file = 'scraping_progress_new.txt'
        
        # If force_rescrape is True, delete the progress file if it exists
        if force_rescrape and os.path.isfile(progress_file):
            os.remove(progress_file)
            print(f"Deleted existing progress file due to force_rescrape flag")
        
        # Load previously scraped dates if resuming
        scraped_dates = set()
        if os.path.isfile(progress_file):
            with open(progress_file, 'r') as f:
                scraped_dates = set(line.strip() for line in f)
        
        # Loop through each date in the range
        total_days = (end_date - start_date).days + 1
        completed_days = len(scraped_dates)
        
        try:
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                
                # Skip if already scraped and not force_rescrape
                if date_str in scraped_dates and not force_rescrape:
                    print(f"Skipping {date_str} - already scraped (use --force to override)")
                    current_date += timedelta(days=1)
                    continue
                
                print(f"\n{'='*50}")
                print(f"Processing date: {date_str} ({completed_days}/{total_days} completed)")
                print(f"{'='*50}\n")
                
                # Scrape data for this specific date
                success = scrape_single_day(current_date, writer)
                
                # Record progress only if successful
                if success:
                    with open(progress_file, 'a') as f:
                        f.write(f"{date_str}\n")
                    if date_str not in scraped_dates:
                        scraped_dates.add(date_str)
                        completed_days += 1
                
                # Move to the next day
                current_date += timedelta(days=1)
                
                # Add delay between days to avoid being blocked
                if current_date <= end_date:
                    delay = 10 + (20 * random.random())  # Random delay between 10-30 seconds
                    print(f"Waiting {delay:.2f} seconds before next date...")
                    time.sleep(delay)
        
        except KeyboardInterrupt:
            print("\nScript interrupted by user. You can resume later from the current date.")
            print(f"To resume, run the script with: --resume {current_date.strftime('%Y-%m-%d')}")
        
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            print(f"You can resume from {current_date.strftime('%Y-%m-%d')}")
        
        finally:
            print(f"Completed scraping {completed_days}/{total_days} days.")
            print(f"All data saved to {csv_filename}")
            if completed_days < total_days:
                print(f"To resume, run with: --resume {current_date.strftime('%Y-%m-%d')}")

def scrape_single_day(target_date, writer):
    """
    Scrape temperature data for a single day
    
    Returns:
        bool: True if data was successfully scraped, False otherwise
    """
    # Set up Chrome options
    chrome_options = Options()
    # Uncomment the line below if you want to run in headless mode
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Add random user agent to avoid detection
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    print("Initializing WebDriver...")
    driver = None
    success = False
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # Format the date for the URL
        date_str = target_date.strftime("%Y-%m-%d")
        url = f"https://www.wunderground.com/history/daily/us/tx/grapevine/KDFW/date/{date_str}"
        
        print(f"Scraping data for {date_str}")
        
        try:
            driver.get(url)
            print(f"Loaded URL: {url}")
            
            # Wait for page to fully load (Weather Underground loads data dynamically)
            print("Waiting for page to load...")
            time.sleep(15)  # Increased wait time for page to fully render
            
            # Save page source for debugging if needed
            os.makedirs("debug", exist_ok=True)
            with open(f"debug/page_source_{date_str}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"Saved page source to debug/page_source_{date_str}.html")
            
            # Try different methods to locate the table
            data_found = False
            
            # Method 1: Look for Daily Observations text
            try:
                print("Method 1: Looking for 'Daily Observations' text...")
                observation_heading = driver.find_element(By.XPATH, "//div[contains(text(), 'Daily Observations')]")
                print("Found 'Daily Observations' heading")
                
                table = driver.find_element(By.XPATH, "//div[contains(text(), 'Daily Observations')]/following::table[1]")
                data_found = process_table(table, writer, date_str, target_date)
            except Exception as error1:
                print(f"Method 1 failed: {str(error1)}")
            
            # Method 2: Look for table with temperature column
            if not data_found:
                try:
                    print("Method 2: Looking for table with temperature column...")
                    table = driver.find_element(By.XPATH, "//th[contains(text(), 'Temperature')]/ancestor::table[1]")
                    data_found = process_table(table, writer, date_str, target_date)
                except Exception as error2:
                    print(f"Method 2 failed: {str(error2)}")
            
            # Method 3: Try to find any table with relevant data
            if not data_found:
                try:
                    print("Method 3: Looking for any tables on the page...")
                    tables = driver.find_elements(By.TAG_NAME, "table")
                    print(f"Found {len(tables)} tables on the page")
                    
                    for i, table in enumerate(tables):
                        print(f"Examining table #{i+1}...")
                        table_html = table.get_attribute("outerHTML")
                        
                        # Look for tables that might contain our data
                        if "Temperature" in table_html or "Time" in table_html:
                            print(f"Table #{i+1} appears to contain weather data")
                            if process_table(table, writer, date_str, target_date):
                                data_found = True
                                break
                    
                    if not data_found:
                        print(f"No data found for {date_str}")
                except Exception as error3:
                    print(f"Method 3 failed: {str(error3)}")
            
            success = data_found
        
        except Exception as e:
            print(f"Error accessing the page for {date_str}: {str(e)}")
    
    except Exception as driver_error:
        print(f"Error initializing WebDriver: {str(driver_error)}")
    
    finally:
        # Close the driver
        if driver:
            driver.quit()
            print("WebDriver closed")
    
    return success

def process_table(table, writer, date_str, target_date):
    """
    Process the table and extract temperature data
    
    Returns:
        bool: True if data was found and processed, False otherwise
    """
    print("Processing table...")
    
    rows = table.find_elements(By.TAG_NAME, "tr")
    print(f"Found {len(rows)} rows in the table")
    
    data_found = False
    
    # Skip the header row if it exists
    for i, row in enumerate(rows[1:], 1):
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            
            if len(cells) >= 2:
                time_val = cells[0].text.strip()
                
                # Check if this is a time entry (some rows might be headers or empty)
                if ":" in time_val or "AM" in time_val or "PM" in time_val:
                    temp_val = cells[1].text.strip().replace('°F', '')
                    
                    # Fix for 12:53 AM entry - assign it to the next day
                    row_date = date_str
                    if time_val == "12:53 AM":
                        # Calculate the next day's date
                        next_day = target_date + timedelta(days=1)
                        row_date = next_day.strftime("%Y-%m-%d")
                        print(f"Fixed 12:53 AM entry: assigning to next day ({row_date})")
                    
                    # Write to CSV
                    writer.writerow({
                        'Date': row_date,
                        'Time': time_val,
                        'Temperature_F': temp_val
                    })
                    print(f"Saved data: {row_date} {time_val}: {temp_val}°F")
                    data_found = True
        
        except Exception as row_error:
            print(f"Error processing row {i}: {str(row_error)}")
    
    if data_found:
        print("Successfully extracted temperature data from the table")
    else:
        print("No usable data found in this table")
    
    return data_found

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Scrape temperature data from Weather Underground')
    parser.add_argument('--resume', type=str, help='Resume from a specific date (YYYY-MM-DD)')
    parser.add_argument('--force', action='store_true', help='Force re-scrape dates even if already scraped')
    args = parser.parse_args()
    
    # Parse resume date if provided
    resume_date = None
    if args.resume:
        try:
            resume_date = datetime.strptime(args.resume, "%Y-%m-%d")
            print(f"Resuming from {resume_date.strftime('%Y-%m-%d')}")
        except ValueError:
            print(f"Invalid date format: {args.resume}. Use YYYY-MM-DD format.")
            sys.exit(1)
    
    # Set the date range for December 12, 2024, to February, 15, 2025
    start_date = datetime(2025, 2, 16)
    end_date = datetime(2025, 2, 22)
    
    # Check if end date is in the future
    today = datetime.now()
    if end_date > today:
        print(f"Warning: End date ({end_date.strftime('%Y-%m-%d')}) is in the future.")
        response = input("Continue with future dates (data may be unavailable) [y/N]? ")
        if response.lower() != 'y':
            end_date = today
            print(f"Adjusted end date to today: {end_date.strftime('%Y-%m-%d')}")
    
    # If force flag is set, notify user
    if args.force:
        print("Force re-scrape flag set - will re-scrape dates even if already in progress file")
    
    # Run the scraper for the date range
    scrape_date_range(start_date, end_date, resume_date, args.force)