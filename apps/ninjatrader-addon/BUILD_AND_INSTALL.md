# Building and Installing NinjaTrader Add-On

## Prerequisites

- **Visual Studio 2019 or later** (required for .NET Framework 4.8)
- **NinjaTrader 8** installed
- **.NET Framework 4.8** (usually comes with Windows)

## Building

### Option 1: Visual Studio (Recommended)

1. **Open Visual Studio**
2. **Open:** `PayoutKingAddOn.csproj`
3. **Restore NuGet packages:**
   - Right-click project → "Restore NuGet Packages"
   - Or: Build → Restore NuGet Packages
4. **Build:**
   - Build → Build Solution (or F6)
   - Or: Right-click project → Build

**Output location:**
- Debug: `bin/Debug/PayoutKingAddOn.dll`
- Release: `bin/Release/PayoutKingAddOn.dll`

### Option 2: MSBuild Command Line

```bash
cd /Users/abhinavala/payout-king/apps/ninjatrader-addon/PayoutKingAddOn
msbuild PayoutKingAddOn.csproj /p:Configuration=Release
```

**Note:** Requires Visual Studio Build Tools or MSBuild installed.

### Option 2: Visual Studio

1. Open `PayoutKingAddOn.csproj` in Visual Studio
2. Right-click project → "Restore NuGet Packages"
3. Build → Build Solution (or F6)
4. DLL will be in `bin/Debug/net8.0/` or `bin/Release/net8.0/`

## Finding NinjaTrader User Data Directory

### Windows

**Default location:**
```
C:\Users\<YourUsername>\Documents\NinjaTrader 8\
```

**Or find it:**
1. Open NinjaTrader
2. Tools → Options → Data
3. Look for "User data folder" path

### Mac (if using Wine/Parallels)

Similar path structure, but may vary based on setup.

## Installation Steps

### 1. Create AddOns Folder (if needed)

```
%USERDATA%\NinjaTrader 8\bin\Custom\AddOns\
```

If `Custom` or `AddOns` folders don't exist, create them.

### 2. Copy DLL

Copy `PayoutKingAddOn.dll` to:
```
%USERDATA%\NinjaTrader 8\bin\Custom\AddOns\PayoutKingAddOn.dll
```

### 3. Copy Dependencies (if needed)

If you see errors about missing DLLs, also copy:
- `Newtonsoft.Json.dll` (if not already in NinjaTrader)
- Any other dependencies

### 4. Create Config Directory

```
%USERDATA%\NinjaTrader 8\PayoutKing\
```

### 5. Create Config File

Create `config.json` in the PayoutKing folder:
```json
{
  "backendUrl": "http://localhost:8000",
  "apiKey": ""
}
```

### 6. Restart NinjaTrader

**Important:** NinjaTrader must be restarted for add-ons to load.

## Verifying Installation

1. **Start NinjaTrader**
2. **Go to:** Tools → Add-Ons
3. **Look for:** "Payout King Add-On"
4. **Enable it** (check the box)
5. **Check Output window:** Tools → Output
6. **Should see:** `✅ Payout King Add-On started`

## Troubleshooting Build Issues

### Missing NuGet Packages

```bash
dotnet restore
```

### Build Errors

Check:
- .NET SDK version (need 8.0+)
- NinjaTrader references (should be in project)
- All files present

### DLL Not Loading

- Check DLL is in correct folder
- Check NinjaTrader was restarted
- Check Output window for errors
- Verify .NET version compatibility

## Next Steps

Once installed:
1. Configure backend URL in config.json
2. Connect account in frontend
3. Enable add-on in NinjaTrader
4. Start testing!

See `NINJATRADER_TESTING_GUIDE.md` for testing instructions.
