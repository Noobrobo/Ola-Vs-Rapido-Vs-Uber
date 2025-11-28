import pandas as pd
import ollama
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json
import re
import unicodedata
import sys
import logging
from logging import StreamHandler

# --- Attempt to import network exceptions (robustness) ---
try:
    from requests.exceptions import ConnectionError, Timeout as TimeoutError
except ImportError:
    from socket import timeout as TimeoutError
    from http.client import HTTPException as ConnectionError 

# --- A. CONFIGURATION & SETUP ---
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, stream=sys.stdout)
logger = logging.getLogger(__name__)

# ===== CONFIGURATION: UPDATE THESE PATHS FOR YOUR PROJECT =====
# 🎯 INPUT: Ensure this path points to your CSV file.
INPUT_CSV = r"C:\Users\Inbox\Downloads\The Riders\Riders_reviews_2025_10.csv"
# 🎯 OUTPUT: The classified data will be saved here.
OUTPUT_CSV = r"C:\Users\Inbox\Downloads\The Riders\Riders_reviews_2025_10_CLASSIFIED.csv"
# 🎯 REVIEW COLUMN: Confirmed to be 'content'
REVIEW_COLUMN = 'content'

MODEL_NAME = 'llama3' 
MAX_WORKERS = 4
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
DEFAULT_NON_INTERACTIVE_ROWS = 100
# =========================

# Column names for classification (RIDE-HAILING THEMES)
CATEGORIES = [
    'Sentiment',
    'Cancellation & Wait Time',
    'Pricing & Payment',
    'Driver & Vehicle Quality',
    'App & Technical Issues',
    'Customer Support',
    'General/Praise',
    'Others'
]

# Standard empty result template
EMPTY_RESULT = {cat: '' for cat in CATEGORIES}

## The Classification Guide is set for RIDE-HAILING topics
CLASSIFICATION_GUIDE = """THEME CATEGORIES (RIDE-HAILING):
A. CANCELLATION & WAIT TIME (4 simple categories)
    - "Driver Cancellation" (Driver refused or cancelled after accepting)
    - "Long Wait Time" (Delayed arrival, waiting too long, no vehicle found)
    - "No Vehicle Available" (No cabs/autos/bikes found, service unavailable)
    - "Mismatch/Incorrect Pickup" (Driver went to wrong location, map pin error)
B. PRICING & PAYMENT (4 simple categories)
    - "Surge & High Fare" (Dynamic pricing, unreasonable cost, price too high)
    - "Refund & Wallet Issues" (Refund pending, money deducted despite cancellation, double charge)
    - "Coupon/Offer Failure" (Discount not applied, promo code invalid)
    - "Toll/Extra Charge Dispute" (Driver demanded extra cash, unexpected toll/fee)
C. DRIVER & VEHICLE QUALITY (4 simple categories)
    - "Rude/Unprofessional Behavior" (Misbehavior, inappropriate language, reckless driving)
    - "Refusal/Asking Destination" (Driver asked destination before starting, refused short ride)
    - "Vehicle Condition" (Dirty car, poor maintenance, hygiene issues)
    - "AC/Comfort Denial" (Driver refused to turn on AC, uncomfortable ride)
D. APP & TECHNICAL ISSUES (3 simple categories - Consolidated)
    - "App Functionality Failure" (Crashing, freezing, slow, booking button not working)
    - "GPS/Tracking Issues" (Inaccurate tracking, map showing wrong location, OTP failure)
    - "Payment System Issue" (Payment failure, system error during transaction)
E. CUSTOMER SUPPORT (3 simple categories)
    - "Unresponsive/Slow Support" (No response from support, took too long to get help)
    - "Poor Resolution" (Issue not solved, unsatisfactory outcome, bot replies)
    - "Good Customer Support" (Helpful, quick response, issue resolved)
F. GENERAL/PRAISE (3 simple categories)
    - "Positive Experience" (Great service, excellent app, recommended, good overall)
    - "Vague Complaint" (Worst app/service, bad experience—no specific reason given)
    - "Feature Request/Suggestion" (Neutral comments suggesting new features or improvements)
G. OTHERS
    - "Unclassifiable" (Use ONLY when review does NOT clearly fit any category above)

CRITICAL RULES:
- The value for each category KEY must be one of the **EXACT** sub-theme labels listed in the guide (e.g., "Driver Cancellation" or "Surge & High Fare").
- If the review does NOT contain the topic for a category, the VALUE **MUST** be an empty string ("").
- Return **ONLY** the JSON object. NO explanations. NO extra text.
"""

def clean_review_text(text):
    """Clean review text to prevent JSON parsing issues"""
    if pd.isna(text) or not text:
        return ""
    
    text = str(text)
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char in '\n\r\t')
    text = text.replace('"', "'").replace('“', "'").replace('”', "'").replace('‘', "'").replace('’', "'")
    text = ' '.join(text.split())
    
    return text.strip()

def classify_review(review_id, review):
    """Classify review using hybrid approach with consistent error handling"""
    if pd.isna(review) or str(review).strip() == '':
        return EMPTY_RESULT.copy()
    
    review_clean = clean_review_text(review)
    if not review_clean:
        return EMPTY_RESULT.copy()
    
    review_lower = review_clean.lower()
    
    # Quick keyword fallback (for speed)
    words = review_lower.split()
    if len(words) == 1:
        word = words[0]
        if word in ['good', 'great', 'excellent', 'amazing', 'best', 'super', 'positive', 'happy', 'fast']:
            result = EMPTY_RESULT.copy()
            result['Sentiment'] = 'Positive'
            result['General/Praise'] = 'Positive Experience'
            return result
        elif word in ['bad', 'worst', 'terrible', 'horrible', 'pathetic', 'rude', 'cancel', 'surge']:
            result = EMPTY_RESULT.copy()
            result['Sentiment'] = 'Negative'
            return result
    
    # Use LLM with retries
    prompt = f"""{CLASSIFICATION_GUIDE}
REVIEW: "{review_clean}"
CRITICAL: 
1. The VALUE for each category KEY must be one of the **EXACT** sub-theme labels listed in the guide (e.g., "Driver Cancellation" or "Surge & High Fare").
2. If the review does NOT contain the topic for a category, the VALUE **MUST** be an empty string ("").
3. Return **ONLY** the JSON object. NO explanations. NO extra text.
{{"Sentiment": "Positive/Negative/Neutral", "Cancellation & Wait Time": "", "Pricing & Payment": "", "Driver & Vehicle Quality": "", "App & Technical Issues": "", "Customer Support": "", "General/Praise": "", "Others": ""}}
"""
    result = EMPTY_RESULT.copy()
    
    for attempt in range(MAX_RETRIES):
        try:
            response = ollama.generate(
                model=MODEL_NAME,
                prompt=prompt,
                format='json',
                options={'temperature': 0.05, 'num_predict': 350} 
            )

            result_text = response['response'].strip()
            parsed = json.loads(result_text)

            for key in CATEGORIES:
                result[key] = str(parsed.get(key, '')).strip()
            return result
            
        except json.JSONDecodeError as e:
            # Consistent 'Error' sentiment for system failures
            if attempt < MAX_RETRIES - 1:
                retry_delay = RETRY_DELAY * (2 ** attempt)
                logger.warning(
                    f"ID {review_id} - JSON Parse Error (Attempt {attempt + 1}/{MAX_RETRIES}). Retrying in {retry_delay}s."
                )
                time.sleep(retry_delay)
                continue
                
            logger.error(
                f"ID {review_id} - JSON Decode Failure. Error: {e}. Last Raw Response: {response.get('response', 'N/A')[:50]}..."
            )
            result['Sentiment'] = 'Error' 
            result['Others'] = 'JSON Parse Error'
            return result
        
        except (ConnectionError, TimeoutError) as e:
            # Consistent 'Error' sentiment for network failures
            if attempt < MAX_RETRIES - 1:
                retry_delay = RETRY_DELAY * (2 ** attempt)
                logger.warning(
                    f"ID {review_id} - Network Error (Attempt {attempt + 1}/{MAX_RETRIES}). Retrying in {retry_delay}s."
                )
                time.sleep(retry_delay)
                continue
                
            logger.critical(
                f"ID {review_id} - Network Failure. Error: {e.__class__.__name__}. Check if Ollama is running."
            )
            result['Sentiment'] = 'Error'
            result['Others'] = 'Network Error'
            return result
            
        except Exception as e:
            # Consistent 'Error' sentiment for fatal errors
            if attempt < MAX_RETRIES - 1:
                retry_delay = RETRY_DELAY * (2 ** attempt)
                logger.warning(
                    f"ID {review_id} - Unexpected Error (Attempt {attempt + 1}/{MAX_RETRIES}). Retrying in {retry_delay}s. Error: {e.__class__.__name__}"
                )
                time.sleep(retry_delay)
                continue
                
            logger.critical(
                f"ID {review_id} - Fatal Error. Error: {e.__class__.__name__}: {e}"
            )
            result['Sentiment'] = 'Error'
            result['Others'] = f'{e.__class__.__name__}'
            return result

    return EMPTY_RESULT.copy()

def process_batch(reviews_series):
    """Process batch of reviews (thread-safe) using index labels."""
    results = []
    for idx, review in reviews_series.items(): 
        classification = classify_review(idx, review) 
        results.append((idx, classification)) 
    return results

def main():
    logger.info("=" * 70)
    logger.info("Ride-Hailing Review Classification - Hybrid (Keywords + LLM)")
    logger.info("=" * 70)

    logger.info(f"\n[1/6] Checking Ollama server connection...")
    try:
        # PING the server and proceed, ignoring the known KeyError issue.
        ollama.list()
        logger.info(f"✓ Ollama server is responding. Attempting to use model '{MODEL_NAME}'.")
    except KeyError:
        logger.warning(f"⚠️ Ollama list check failed with KeyError. Assuming server is up and proceeding with model '{MODEL_NAME}'.")
    except Exception as e:
        logger.critical(f"✗ Ollama connection failed. Start Ollama first: ollama serve. Error: {e.__class__.__name__}")
        return

    logger.info(f"\n[2/6] Loading {INPUT_CSV}...")
    try:
        df_full = pd.read_csv(INPUT_CSV)
        df_full.reset_index(drop=True, inplace=True)
        logger.info(f"✓ Loaded {len(df_full)} rows")
    except Exception as e:
        logger.critical(f"✗ Error loading CSV: {e}")
        return

    if REVIEW_COLUMN not in df_full.columns:
        logger.critical(f"✗ Column '{REVIEW_COLUMN}' not found in CSV.")
        return

    logger.info(f"\n[3/6] Dataset: {len(df_full)} reviews")
    
    # Handle user input for processing subset
    if sys.stdin.isatty():
        try:
            user_input = input(f"Process how many? (number or 'all', default {DEFAULT_NON_INTERACTIVE_ROWS} for non-interactive): ")
            if user_input.lower() == 'all':
                rows_to_process = len(df_full)
            else:
                rows_to_process = min(int(user_input), len(df_full))
        except:
            rows_to_process = min(DEFAULT_NON_INTERACTIVE_ROWS, len(df_full))
    else:
        rows_to_process = min(DEFAULT_NON_INTERACTIVE_ROWS, len(df_full))
        logger.info(f"Non-interactive run detected. Processing first {rows_to_process} rows.")

    df_processing = df_full.head(rows_to_process).copy()
    logger.info(f"✓ Processing {len(df_processing)} reviews")
    
    logger.info(f"\n[4/6] Classifying with {MAX_WORKERS} workers...")
    
    # Initialize the new theme columns in the processing subset (df_processing)
    for cat in CATEGORIES:
        df_processing[cat] = ''

    total_reviews = len(df_processing)
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        index_labels = df_processing.index.tolist()
        chunk_size = max(1, len(index_labels) // MAX_WORKERS)
        
        for i in range(0, len(index_labels), chunk_size):
            chunk_labels = index_labels[i:i + chunk_size]
            reviews_slice = df_processing.loc[chunk_labels, REVIEW_COLUMN]
            futures.append(executor.submit(process_batch, reviews_slice))

        completed = 0
        for future in as_completed(futures):
            batch_results = future.result()
            
            for row_idx, cls in batch_results:
                for cat in CATEGORIES:
                    # Update the processing dataframe with results
                    df_processing.at[row_idx, cat] = cls.get(cat, '')

            completed += len(batch_results)
            elapsed = time.time() - start_time
            rate = completed / elapsed if elapsed > 0 else 0
            eta = (total_reviews - completed) / rate / 60 if rate > 0 else 0
            
            logger.info(f"Progress: {completed}/{total_reviews} ({completed/total_reviews*100:.1f}%) | Rate: {rate:.2f}/sec | ETA: {eta:.1f} min")

    logger.info(f"\n[5/6] Complete! Total time: {(time.time()-start_time)/60:.1f} min")

    # --- THE CRITICAL FIX: Transferring new columns from df_processing to df_full ---
    logger.info(f"\nAdding {len(CATEGORIES)} new classified columns to output dataframe...")
    
    # Loop through the new classification columns and add them directly to df_full
    for cat in CATEGORIES:
        # Use .loc to assign the new column data based on aligned index labels
        df_full.loc[df_processing.index, cat] = df_processing[cat]

    logger.info("\n[6/6] Summary:")
    sentiment_counts = df_full['Sentiment'].value_counts(dropna=False) # Use df_full for summary
    total_processed = len(df_processing) # Total processed rows for percentages
    for s, c in sentiment_counts.items():
        s_display = 'N/A' if pd.isna(s) or s == '' else s
        logger.info(f"  {s_display:<10}: {c:>5} ({c/total_processed*100:.1f}%)")

    logger.info("\nTheme Counts:")
    theme_categories = [cat for cat in CATEGORIES if cat != 'Sentiment' and cat != 'Others']
    for cat in theme_categories:
        n = df_full[cat].astype(str).str.strip().ne('').sum() # Use df_full for summary
        if n > 0:
            logger.info(f"  {cat:<25}: {n:>5} ({n/total_processed*100:.1f}%)")
        else:
            logger.info(f"  {cat:<25}: {0:>5} (0.0%)")

    logger.info(f"\nSaving to {OUTPUT_CSV}...")
    
    # Save df_full which now contains the new columns
    df_full.to_csv(OUTPUT_CSV, index=False) 
    logger.info("✓ Saved!")

    logger.info("\n" + "=" * 70)
    logger.info(f"Done! Check {OUTPUT_CSV}")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()