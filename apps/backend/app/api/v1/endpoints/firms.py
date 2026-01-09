"""
Prop firm information endpoints.

Provides information about supported firms and their rules.
"""

from fastapi import APIRouter
from app.schemas.firm import FirmInfo, FirmListResponse, AccountTypeInfo, AccountTypeListResponse
from app.services.rule_loader import RuleLoaderService

router = APIRouter()


@router.get("/", response_model=FirmListResponse)
async def list_firms():
    """
    Get list of all supported prop firms.
    
    Returns information about each firm including:
    - Firm name and ID
    - Supported account types
    - Rules summary
    """
    rule_loader = RuleLoaderService()
    supported_firms = rule_loader.get_supported_firms()
    
    firms = []
    
    # Apex
    if "apex" in supported_firms:
        firms.append(FirmInfo(
            id="apex",
            name="apex",
            display_name="Apex Trader Funding",
            supported_account_types=["eval", "pa", "funded"],
            description="5% trailing drawdown, no daily loss limit, news trading allowed",
            rules_summary={
                "trailing_drawdown": "5% (intraday, includes unrealized PnL)",
                "daily_loss_limit": "None",
                "consistency": "None",
                "news_trading": "Allowed",
            }
        ))
    
    # Topstep
    if "topstep" in supported_firms:
        firms.append(FirmInfo(
            id="topstep",
            name="topstep",
            display_name="Topstep",
            supported_account_types=["eval", "pa", "funded"],
            description="End-of-day drawdown, $1000 daily loss limit, 50% consistency rule",
            rules_summary={
                "trailing_drawdown": "4% (end-of-day, balance only)",
                "daily_loss_limit": "$1000 for $50k account",
                "consistency": "50% during evaluation",
                "news_trading": "Allowed",
            }
        ))
    
    # MFF
    if "mff" in supported_firms:
        firms.append(FirmInfo(
            id="mff",
            name="mff",
            display_name="My Funded Futures",
            supported_account_types=["eval", "pa", "funded"],
            description="5% trailing drawdown, ~5% daily loss limit",
            rules_summary={
                "trailing_drawdown": "5% (varies by account type)",
                "daily_loss_limit": "~5% of account balance",
                "consistency": "Varies by account type",
                "news_trading": "Allowed",
            }
        ))
    
    # Bulenox
    if "bulenox" in supported_firms:
        firms.append(FirmInfo(
            id="bulenox",
            name="bulenox",
            display_name="Bulenox",
            supported_account_types=["eval", "pa", "funded"],
            description="5% trailing drawdown, 4% daily loss limit, 40% consistency rule",
            rules_summary={
                "trailing_drawdown": "5% (intraday, includes unrealized PnL)",
                "daily_loss_limit": "4% of account balance",
                "consistency": "40% (no single day > 40% of total profit)",
                "news_trading": "Not allowed",
            }
        ))
    
    # TakeProfitTrader
    if "takeprofit" in supported_firms:
        firms.append(FirmInfo(
            id="takeprofit",
            name="takeprofit",
            display_name="TakeProfitTrader",
            supported_account_types=["eval", "pa", "funded"],
            description="End-of-day drawdown (eval), trailing drawdown (funded), 50% consistency during eval",
            rules_summary={
                "trailing_drawdown": "5% (end-of-day during eval, trailing when funded)",
                "daily_loss_limit": "Varies by account type",
                "consistency": "50% during evaluation, none when funded",
                "news_trading": "Not allowed",
            }
        ))
    
    return FirmListResponse(firms=firms)


@router.get("/account-types", response_model=AccountTypeListResponse)
async def list_account_types():
    """
    Get list of account types.
    
    Returns:
        List of account types (eval, pa, funded)
    """
    account_types = [
        AccountTypeInfo(
            id="eval",
            name="eval",
            display_name="Evaluation",
            description="Challenge/evaluation account - must pass to get funded",
        ),
        AccountTypeInfo(
            id="pa",
            name="pa",
            display_name="PA (Payout Account)",
            description="Payout account - can request payouts after passing evaluation",
        ),
        AccountTypeInfo(
            id="funded",
            name="funded",
            display_name="Funded",
            description="Fully funded account - live trading with profit splits",
        ),
    ]
    
    return AccountTypeListResponse(account_types=account_types)


@router.get("/{firm_id}/rules")
async def get_firm_rules(firm_id: str, account_type: str = "eval"):
    """
    Get detailed rules for a specific firm and account type.
    
    Args:
        firm_id: Firm ID (apex, topstep, mff, bulenox, takeprofit)
        account_type: Account type (eval, pa, funded)
        
    Returns:
        Detailed rule set
    """
    rule_loader = RuleLoaderService()
    
    try:
        rules = await rule_loader.get_rules(firm_id, account_type)
        
        # Convert to dict for response
        rules_dict = {}
        
        if rules.trailing_drawdown:
            rules_dict["trailing_drawdown"] = {
                "enabled": rules.trailing_drawdown.enabled,
                "max_drawdown_percent": float(rules.trailing_drawdown.max_drawdown_percent),
                "include_unrealized_pnl": rules.trailing_drawdown.include_unrealized_pnl,
                "description": "Maximum trailing drawdown percentage",
            }
        
        if rules.daily_loss_limit:
            rules_dict["daily_loss_limit"] = {
                "enabled": rules.daily_loss_limit.enabled,
                "max_loss_amount": float(rules.daily_loss_limit.max_loss_amount),
                "reset_time": rules.daily_loss_limit.reset_time,
                "timezone": rules.daily_loss_limit.timezone,
                "description": "Maximum daily loss allowed",
            }
        
        if rules.overall_max_loss:
            rules_dict["overall_max_loss"] = {
                "enabled": rules.overall_max_loss.enabled,
                "max_loss_amount": float(rules.overall_max_loss.max_loss_amount),
                "from_starting_balance": rules.overall_max_loss.from_starting_balance,
                "description": "Overall maximum loss limit",
            }
        
        return {
            "firm": firm_id,
            "account_type": account_type,
            "rules": rules_dict,
        }
    except ValueError as e:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

