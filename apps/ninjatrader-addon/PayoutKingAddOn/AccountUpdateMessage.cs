/*
 * AccountUpdateMessage.cs
 * 
 * Message schema for AccountUpdate - matches backend interface exactly
 * This schema is SACRED - do not modify without updating backend
 */

using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace NinjaTrader.NinjaScript.AddOns
{
    /// <summary>
    /// AccountUpdate message - matches AccountSnapshot interface in rules engine
    /// This is the FROZEN interface - changes require backend updates
    /// </summary>
    public class AccountUpdateMessage
    {
        [JsonProperty("accountId")]
        public string AccountId { get; set; }

        [JsonProperty("timestamp")]
        public long Timestamp { get; set; } // Unix timestamp in milliseconds

        [JsonProperty("equity")]
        public decimal Equity { get; set; }

        [JsonProperty("balance")]
        public decimal Balance { get; set; }

        [JsonProperty("realizedPnl")]
        public decimal RealizedPnl { get; set; }

        [JsonProperty("unrealizedPnl")]
        public decimal UnrealizedPnl { get; set; }

        [JsonProperty("highWaterMark")]
        public decimal HighWaterMark { get; set; }

        [JsonProperty("dailyPnl")]
        public decimal DailyPnl { get; set; }

        [JsonProperty("startingBalance")]
        public decimal StartingBalance { get; set; }

        [JsonProperty("openPositions")]
        public List<PositionMessage> OpenPositions { get; set; } = new List<PositionMessage>();

        [JsonProperty("dailyPnlHistory")]
        public Dictionary<string, decimal> DailyPnlHistory { get; set; } = new Dictionary<string, decimal>();
    }

    /// <summary>
    /// Position message - matches PositionSnapshot interface
    /// </summary>
    public class PositionMessage
    {
        [JsonProperty("symbol")]
        public string Symbol { get; set; }

        [JsonProperty("quantity")]
        public int Quantity { get; set; } // Positive = long, negative = short

        [JsonProperty("avgPrice")]
        public decimal AvgPrice { get; set; }

        [JsonProperty("currentPrice")]
        public decimal CurrentPrice { get; set; }

        [JsonProperty("unrealizedPnl")]
        public decimal UnrealizedPnl { get; set; }

        [JsonProperty("openedAt")]
        public long OpenedAt { get; set; } // Unix timestamp in milliseconds

        [JsonProperty("peakUnrealizedLoss")]
        public decimal PeakUnrealizedLoss { get; set; } // For MAE tracking
    }
}
