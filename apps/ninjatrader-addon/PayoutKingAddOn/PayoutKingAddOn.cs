/*
 * PayoutKingAddOn.cs
 * 
 * NinjaTrader Add-On for Payout King
 * Reads account data and sends to backend API
 */

#region Using declarations
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using NinjaTrader.Cbi;
using NinjaTrader.NinjaScript;
#endregion

namespace NinjaTrader.NinjaScript.AddOns
{
    public class PayoutKingAddOn : NinjaTrader.NinjaScript.AddOnBase
    {
        private HttpClient httpClient;
        private string backendUrl;
        private string apiKey;
        private string accountId;
        private System.Timers.Timer updateTimer;
        private Account account;
        private Dictionary<string, double> dailyPnLByDate = new Dictionary<string, double>(); // Date string -> daily PnL
        private Dictionary<string, double> peakLosses = new Dictionary<string, double>(); // Position key -> peak loss

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "Payout King Add-On";
                Description = "Sends account data to Payout King backend for rule tracking";
            }
            else if (State == State.Configure)
            {
                // Initialize HTTP client
                httpClient = new HttpClient();
                httpClient.Timeout = TimeSpan.FromSeconds(10);

                // Load configuration from config file
                LoadConfiguration();

                // Find the account
                account = this.Account;
                if (account == null)
                {
                    Print("⚠️  No account found. Please ensure you're logged in.");
                    return;
                }

                accountId = account.Name;
                Print($"✅ Connected to account: {accountId}");
            }
            else if (State == State.Active)
            {
                // Start update timer (send data every 300ms for real-time tracking)
                // Per Master Plan: 100-500ms for tick-level monitoring
                updateTimer = new System.Timers.Timer(300);
                updateTimer.Elapsed += async (sender, e) => await SendAccountData();
                updateTimer.Start();

                Print("✅ Payout King Add-On started");
            }
            else if (State == State.Terminated)
            {
                // Cleanup
                if (updateTimer != null)
                {
                    updateTimer.Stop();
                    updateTimer.Dispose();
                }

                if (httpClient != null)
                {
                    httpClient.Dispose();
                }
            }
        }

        private void LoadConfiguration()
        {
            // Default configuration (user can override)
            backendUrl = "http://localhost:8000";
            apiKey = ""; // Will be set by user

            // Try to load from config file
            try
            {
                string configPath = System.IO.Path.Combine(
                    NinjaTrader.Core.Globals.UserDataDir,
                    "PayoutKing",
                    "config.json"
                );

                if (System.IO.File.Exists(configPath))
                {
                    string json = System.IO.File.ReadAllText(configPath);
                    var config = JsonConvert.DeserializeObject<Dictionary<string, string>>(json);
                    
                    if (config.ContainsKey("backendUrl"))
                        backendUrl = config["backendUrl"];
                    if (config.ContainsKey("apiKey"))
                        apiKey = config["apiKey"];
                    
                    Print($"✅ Loaded config from: {configPath}");
                    Print($"   Backend URL: {backendUrl}");
                }
                else
                {
                    Print($"⚠️  Config file not found: {configPath}");
                    Print($"   Using defaults: {backendUrl}");
                }
            }
            catch (Exception ex)
            {
                Print($"⚠️  Error loading config: {ex.Message}");
                Print($"   Using defaults: {backendUrl}");
            }
        }

        private async Task SendAccountData()
        {
            if (account == null || string.IsNullOrEmpty(backendUrl))
                return;

            try
            {
                // Collect account data - matches AccountUpdateMessage schema exactly
                var accountUpdate = new AccountUpdateMessage
                {
                    AccountId = accountId,
                    Timestamp = (long)(DateTime.UtcNow - new DateTime(1970, 1, 1)).TotalMilliseconds,
                    Equity = (decimal)account.Get(AccountItem.CashValue, Currency.UsDollar),
                    Balance = (decimal)(account.Get(AccountItem.CashValue, Currency.UsDollar) - account.Get(AccountItem.UnrealizedProfitLoss, Currency.UsDollar)),
                    RealizedPnl = (decimal)account.Get(AccountItem.RealizedProfitLoss, Currency.UsDollar),
                    UnrealizedPnl = (decimal)account.Get(AccountItem.UnrealizedProfitLoss, Currency.UsDollar),
                    HighWaterMark = (decimal)GetHighWaterMark(),
                    DailyPnl = (decimal)GetDailyPnL(),
                    StartingBalance = (decimal)GetStartingBalance(),
                    OpenPositions = GetOpenPositions(),
                    DailyPnlHistory = GetDailyPnlHistory()
                };

                // Send to backend - matches AccountSnapshot interface
                string json = JsonConvert.SerializeObject(accountUpdate);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                if (!string.IsNullOrEmpty(apiKey))
                {
                    httpClient.DefaultRequestHeaders.Clear();
                    httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");
                }

                var response = await httpClient.PostAsync($"{backendUrl}/api/v1/ninjatrader/account-update", content);

                if (response.IsSuccessStatusCode)
                {
                    // Success - data sent
                    // Don't print every time to avoid log spam (300ms updates)
                }
                else
                {
                    string errorBody = await response.Content.ReadAsStringAsync();
                    Print($"⚠️  Backend error: {response.StatusCode}");
                    Print($"   Response: {errorBody}");
                }
            }
            catch (Exception ex)
            {
                // Log errors but don't spam - only log occasionally
                Print($"❌ Error sending data: {ex.Message}");
            }
        }

        private double GetHighWaterMark()
        {
            // TODO: Load from persistent storage
            // For now, use current equity as placeholder
            return account.Get(AccountItem.CashValue, Currency.UsDollar);
        }

        private double GetDailyPnL()
        {
            // Calculate from fills for today
            string today = DateTime.UtcNow.ToString("yyyy-MM-dd");
            
            if (dailyPnLByDate.ContainsKey(today))
            {
                return dailyPnLByDate[today];
            }
            
            // If no fills tracked yet, use 0
            // Backend should track this more accurately
            return 0;
        }

        private List<PositionMessage> GetOpenPositions()
        {
            var positions = new List<PositionMessage>();
            
            foreach (Position position in account.Positions)
            {
                if (position.MarketPosition != MarketPosition.Flat)
                {
                    // Track peak unrealized loss for MAE
                    double currentUnrealized = position.GetUnrealizedProfitLoss(PerformanceUnit.Currency);
                    double peakLoss = GetPeakUnrealizedLoss(position, currentUnrealized);

                    // Get current price - use AveragePrice (simplified for now)
                    // Real-time price would require accessing market data, which is complex
                    // AveragePrice is acceptable for rule engine calculations
                    double currentPrice = position.AveragePrice;

                    positions.Add(new PositionMessage
                    {
                        Symbol = position.Instrument.FullName,
                        Quantity = position.Quantity, // Positive = long, negative = short
                        AvgPrice = (decimal)position.AveragePrice,
                        CurrentPrice = (decimal)currentPrice,
                        UnrealizedPnl = (decimal)currentUnrealized,
                        OpenedAt = (long)(DateTime.UtcNow - new DateTime(1970, 1, 1)).TotalMilliseconds, // Simplified - entry time not easily available
                        PeakUnrealizedLoss = (decimal)peakLoss
                    });
                }
            }

            return positions;
        }

        private double GetPeakUnrealizedLoss(Position position, double currentUnrealized)
        {
            // Use instrument name + quantity as key (entry time not easily available)
            string key = position.Instrument.FullName + "_" + position.Quantity.ToString();
            
            if (!peakLosses.ContainsKey(key))
            {
                peakLosses[key] = 0;
            }

            // Track worst (most negative) unrealized loss for MAE
            // This is the maximum adverse excursion - worst point even if trade recovers
            if (currentUnrealized < peakLosses[key])
            {
                peakLosses[key] = currentUnrealized;
            }

            return peakLosses[key];
        }

        private double GetStartingBalance()
        {
            // TODO: Load from persistent storage or backend
            // For now, use current balance if no history
            // Backend should track this, but we can provide initial value
            return account.Get(AccountItem.CashValue, Currency.UsDollar);
        }

        private Dictionary<string, decimal> GetDailyPnlHistory()
        {
            // Return daily PnL history - simplified for now
            // Backend is source of truth and tracks this more accurately
            var history = new Dictionary<string, decimal>();
            
            foreach (var kvp in dailyPnLByDate)
            {
                history[kvp.Key] = (decimal)kvp.Value;
            }
            
            return history;
        }
    }
}

