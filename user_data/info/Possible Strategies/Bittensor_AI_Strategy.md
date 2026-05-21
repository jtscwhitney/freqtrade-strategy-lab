# Bittensor (TAO) Automated Trading Strategy Specification

## Overview
This document outlines the automated trading and staking strategy for the Bittensor (TAO) ecosystem, as extracted from Lewis Jackson's methodology (based on Mark Jeffrey's research). The strategy is explicitly designed to be implemented by an AI coding assistant (like Claude Code) or an automated Python agent interacting with the Bittensor Command Line Interface (CLI).

## Tech Stack & Architecture
* **Orchestration Engine:** AI Agent (e.g., Claude Code in terminal) or scheduled Python scripts.
* **Blockchain Interface:** Bittensor CLI (`btcli`) to handle wallet creation, staking, and subnet swaps.
* **Data Feed:** CoinGecko API (Free tier) for tracking TAO and subnet prices.
* **Alerting System:** Telegram Bot API (via BotFather) for mobile trade notifications.
* **Security:** Local `.env` file. **Crucially, this file must securely store:**
    * Wallet Mnemonic phrase
    * CoinGecko API Key
    * Telegram Bot Token
    * Telegram Chat ID

## Portfolio Allocation Map
The portfolio is divided into a 50/50 split between low-risk base yield and higher-risk "Alpha" subnets.

### 1. Root Staking (50%)
* **Allocation:** 50% of the total TAO capital.
* **Action:** Staked directly on the Bittensor root network. 
* **Purpose:** To capture steady, low-risk emissions and compound yield over time (similar to an index fund approach).

### 2. Subnet "Alpha" Tokens (50%)
* **Allocation:** 50% of the total TAO capital distributed across selected subnets.
* **Target Subnets (as a % of the total overall portfolio):**
    * **Shoots (SN64):** 16.5%
    * **Ridges (SN62):** 11.0%
    * **Targon (SN4):** 9.5%
    * **Hippius (SN75):** 7.0%
    * **Nova (SN68):** 3.5%
    * **Precog / Cortex.t (SN55):** 2.5%

*(Note: These subnets act as high-potential "angel investments" where success directly influences the TAO ecosystem.)*

## Algorithmic Execution Rules

### Entry Strategy: Dollar Cost Averaging (DCA) on Dips
* **Data Polling:** Query the CoinGecko API at regular intervals (e.g., 3:00 AM, 6:00 AM).
* **Condition:** If the price of TAO experiences a **3% drop in a 24-hour period**.
* **Action:** Execute 1 buy tranche. (The strategy limits entries to a total of 5 separate tranches/purchases to manage risk).
* **Execution:** Convert TAO into the target subnet tokens matching the predefined allocation percentages.

### Exit Strategy: Algorithmic Profit Taking
* **Condition:** If a specific Subnet token's price increases by **10% in a single 24-hour period**.
* **Action:** Sell **10%** of the position in *that specific subnet* back into TAO.
* **Golden Rule (The Moonbag):** Never sell the final **10%** of the initial subnet investment. Leave this remainder permanently invested for long-term "generational wealth" potential.
* **Capital Flow:** Profits from subnet token sales are strictly held/compounded in TAO, not converted to fiat.

### Event-Driven Exit Catalysts (Sentiment/News Monitoring)
The agent should be prepared to take risk off the table if the following catalysts occur:
1.  **Ecosystem Bridges:** Solana opening up the ability for retail to easily buy subnets (often a "sell the news" event).
2.  **CEX Listings:** Centralized exchanges listing specific subnets.
3.  **Whale Tracking:** Significant movements by Mark Jeffrey's hedge fund or Barry Silbert's wallets.
4.  **Revenue Milestones:** Subnets hitting major revenue generation targets.

## AI Implementation Instructions (System Prompt)
*To build this system using an AI tool, feed it the following instructions:*

> "You are an automated cryptocurrency trading agent. Read the above Bittensor (TAO) strategy. 
> 1. Set up a local Python environment and a `.env` template. 
> 2. Write a Python script (`price_monitor.py`) to hit the CoinGecko API to track TAO, SN64, SN62, SN4, SN75, SN68, and SN55. 
> 3. Write an evaluation script (`tao_alerts.py`) that implements the DCA logic: Trigger a buy using `btcli` when TAO drops 3% in 24h (up to 5 total tranches). 
> 4. Implement the profit-taking logic: Trigger a sell of 10% of a subnet position back to TAO when that subnet rises 10% in 24h, keeping a minimum 10% core position. 
> 5. Create a `telegram_bot.py` script to send me a summary message every time a trade is simulated or executed."
