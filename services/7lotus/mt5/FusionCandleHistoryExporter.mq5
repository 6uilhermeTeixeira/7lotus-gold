#property strict
#property script_show_inputs
#property version "1.00"
#property description "Exports closed Fusion Markets XAUUSD M5 candles. No trading functions."

input string CaptureSymbol = "XAUUSD";
input int MaximumBars = 2000000;
input int ChunkBars = 5000;

void OnStart()
  {
   if(MaximumBars < 1 || ChunkBars < 1 || ChunkBars > 20000)
     {
      Print("Invalid bar limits.");
      return;
     }
   string server = AccountInfoString(ACCOUNT_SERVER);
   for(int attempt = 0; attempt < 180 && server == ""; attempt++)
     {
      Sleep(1000);
      server = AccountInfoString(ACCOUNT_SERVER);
     }
   if(StringFind(server, "Fusion") < 0)
     {
      PrintFormat("Export refused: connected MT5 server is not identified as Fusion Markets: %s", server);
      return;
     }
   if(!SymbolSelect(CaptureSymbol, true))
     {
      PrintFormat("Symbol unavailable: %s, error=%d", CaptureSymbol, GetLastError());
      return;
     }
   int digits = (int)SymbolInfoInteger(CaptureSymbol, SYMBOL_DIGITS);
   string directory = "1lotus-candles\\fusion";
   FolderCreate(directory, FILE_COMMON);
   string prefix = directory + "\\" + CaptureSymbol + "-M5-candles";
   string partial = prefix + ".part.csv";
   string ready = prefix + ".ready.csv";
   int handle = FileOpen(partial, FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON, ',');
   if(handle == INVALID_HANDLE)
     {
      PrintFormat("CSV open failed: %d", GetLastError());
      return;
     }
   FileWrite(handle, "server_time", "open", "high", "low", "close", "tick_volume", "spread_points", "real_volume");
   datetime target = TimeCurrent() - 5 * 366 * 86400;
   MqlRates history[];
   int available = 0;
   datetime first_loaded = 0;
   for(int attempt = 0; attempt < 36; attempt++)
     {
      ResetLastError();
      available = CopyRates(CaptureSymbol, PERIOD_M5, target, TimeCurrent(), history);
      if(available > 0)
        {
         first_loaded = history[0].time;
         if(first_loaded <= target + 86400)
            break;
        }
      Sleep(5000);
     }
   int maximum = MathMin(MaximumBars, available);
   int exported = 0;
   datetime latest = 0;
   datetime earliest = 0;
   for(int position = maximum - 1; position >= 0; )
     {
      int lower = MathMax(0, position - ChunkBars + 1);
      for(int index = position; index >= lower; index--)
        {
         datetime stamp = history[index].time;
         if(stamp + PeriodSeconds(PERIOD_M5) > TimeCurrent())
            continue;
         if(latest == 0)
            latest = stamp;
         earliest = stamp;
         FileWrite(handle,
                   TimeToString(stamp, TIME_DATE|TIME_SECONDS),
                   DoubleToString(history[index].open, digits),
                   DoubleToString(history[index].high, digits),
                   DoubleToString(history[index].low, digits),
                   DoubleToString(history[index].close, digits),
                   IntegerToString(history[index].tick_volume),
                   IntegerToString(history[index].spread),
                   DoubleToString(history[index].real_volume, 8));
         exported++;
        }
      position = lower - 1;
     }
   FileClose(handle);
   if(exported == 0)
     {
      FileDelete(partial, FILE_COMMON);
      Print("No closed XAUUSD M5 candles available. Check connection and MT5 history sync.");
      return;
     }
   if(!FileMove(partial, FILE_COMMON, ready, FILE_COMMON|FILE_REWRITE))
     {
      PrintFormat("CSV finalize failed: %d", GetLastError());
      return;
     }
   PrintFormat("Fusion M5 export complete: server=%s symbol=%s bars=%d first=%s last=%s common_file=%s",
               server, CaptureSymbol, exported,
               TimeToString(earliest, TIME_DATE|TIME_SECONDS),
               TimeToString(latest, TIME_DATE|TIME_SECONDS), ready);
  }
