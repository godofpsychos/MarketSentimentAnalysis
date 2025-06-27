#!/usr/bin/env python3
"""
Run All Fundamental Analysis Indicators
Main script to execute all indicator calculations
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add paths for imports
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / 'utils'))
sys.path.append(str(current_dir / 'indicators'))

# Import data loader
from data_loader import FinancialDataLoader

# Import all indicator calculators
try:
    from profitability_indicators import ProfitabilityIndicators
    from valuation_indicators import ValuationIndicators
    from growth_indicators import GrowthIndicators
    from liquidity_indicators import LiquidityIndicators
    # Import other indicators as they're created
    profitability_available = True
    valuation_available = True
    growth_available = True
    liquidity_available = True
except ImportError as e:
    print(f"⚠️  Some indicators not available: {e}")
    profitability_available = False
    valuation_available = False
    growth_available = False
    liquidity_available = False

def run_all_fundamental_analysis():
    """Run all fundamental analysis indicators"""
    print("🚀 STARTING COMPREHENSIVE FUNDAMENTAL ANALYSIS")
    print("=" * 80)
    
    start_time = datetime.now()
    
    # Initialize data loader
    print("📊 Loading financial data...")
    loader = FinancialDataLoader()
    companies = loader.load_all_companies()
    
    if not companies:
        print("❌ No financial data found!")
        print("Please ensure financial data is available in '../financial_reports/data' directory")
        return
    
    print(f"✅ Loaded data for {len(companies)} companies")
    print()
    
    # Create output directories
    output_base = Path("outputs")
    output_base.mkdir(exist_ok=True)
    
    results_summary = {}
    
    # 1. Profitability Analysis
    if profitability_available:
        try:
            print("🎯 Running Profitability Analysis...")
            profitability_calc = ProfitabilityIndicators(loader)
            prof_results = profitability_calc.run_analysis_for_all_companies()
            results_summary['profitability'] = {
                'completed': True,
                'companies': len(prof_results[0]) if prof_results[0] is not None else 0
            }
            print("✅ Profitability analysis completed\n")
        except Exception as e:
            print(f"❌ Error in profitability analysis: {e}\n")
            results_summary['profitability'] = {'completed': False, 'error': str(e)}
    
    # 2. Valuation Analysis
    if valuation_available:
        try:
            print("💰 Running Valuation Analysis...")
            valuation_calc = ValuationIndicators(loader)
            val_results = valuation_calc.run_analysis_for_all_companies()
            results_summary['valuation'] = {
                'completed': True,
                'companies': len(val_results[0]) if val_results[0] is not None else 0
            }
            print("✅ Valuation analysis completed\n")
        except Exception as e:
            print(f"❌ Error in valuation analysis: {e}\n")
            results_summary['valuation'] = {'completed': False, 'error': str(e)}
    
    # 3. Growth Analysis
    if growth_available:
        try:
            print("📈 Running Growth Analysis...")
            growth_calc = GrowthIndicators(loader)
            growth_results = growth_calc.run_analysis_for_all_companies()
            results_summary['growth'] = {
                'completed': True,
                'companies': len(growth_results[0]) if growth_results[0] is not None else 0
            }
            print("✅ Growth analysis completed\n")
        except Exception as e:
            print(f"❌ Error in growth analysis: {e}\n")
            results_summary['growth'] = {'completed': False, 'error': str(e)}
    
    # 4. Liquidity Analysis
    if liquidity_available:
        try:
            print("💧 Running Liquidity Analysis...")
            liquidity_calc = LiquidityIndicators(loader)
            liq_results = liquidity_calc.run_analysis_for_all_companies()
            results_summary['liquidity'] = {
                'completed': True,
                'companies': len(liq_results[0]) if liq_results[0] is not None else 0
            }
            print("✅ Liquidity analysis completed\n")
        except Exception as e:
            print(f"❌ Error in liquidity analysis: {e}\n")
            results_summary['liquidity'] = {'completed': False, 'error': str(e)}
    
    # Calculate execution time
    end_time = datetime.now()
    execution_time = end_time - start_time
    
    # Generate overall summary
    generate_execution_summary(results_summary, execution_time, len(companies))
    
    print("🎉 FUNDAMENTAL ANALYSIS COMPLETED!")
    print("=" * 50)
    print(f"⏱️  Total execution time: {execution_time}")
    print(f"📁 Results saved in: {output_base.absolute()}")

def generate_execution_summary(results_summary, execution_time, total_companies):
    """Generate and save execution summary"""
    summary = []
    summary.append("📊 FUNDAMENTAL ANALYSIS EXECUTION SUMMARY")
    summary.append("=" * 60)
    summary.append(f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append(f"Total Companies Analyzed: {total_companies}")
    summary.append(f"Total Execution Time: {execution_time}")
    summary.append("")
    
    # Analysis Results
    summary.append("📈 ANALYSIS RESULTS:")
    summary.append("-" * 25)
    
    for analysis_type, result in results_summary.items():
        if result['completed']:
            summary.append(f"✅ {analysis_type.title()}: {result['companies']} companies")
        else:
            summary.append(f"❌ {analysis_type.title()}: Failed - {result.get('error', 'Unknown error')}")
    
    summary.append("")
    
    # Output directories
    summary.append("📁 OUTPUT DIRECTORIES:")
    summary.append("-" * 25)
    output_dirs = [
        "outputs/profitability/",
        "outputs/valuation/", 
        "outputs/growth/",
        "outputs/liquidity/",
        "outputs/efficiency/",
        "outputs/leverage/",
        "outputs/quality/",
        "outputs/momentum/",
        "outputs/risk/",
        "outputs/sector_specific/"
    ]
    
    for output_dir in output_dirs:
        if Path(output_dir).exists():
            file_count = len(list(Path(output_dir).glob("*")))
            summary.append(f"📂 {output_dir}: {file_count} files")
    
    summary.append("")
    summary.append("🔍 NEXT STEPS:")
    summary.append("-" * 15)
    summary.append("1. Review individual analysis summaries in each output directory")
    summary.append("2. Examine CSV files for detailed metrics")
    summary.append("3. Use JSON files for programmatic analysis")
    summary.append("4. Run sector-specific analysis for deeper insights")
    summary.append("5. Generate company-specific reports using report_generator.py")
    
    # Save summary
    summary_text = "\n".join(summary)
    
    output_path = Path("outputs/execution_summary.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary_text)
    
    print(summary_text)
    print(f"\n💾 Execution summary saved: {output_path}")

def run_specific_indicator(indicator_name):
    """Run a specific indicator"""
    print(f"🎯 Running {indicator_name} Analysis Only")
    print("=" * 50)
    
    # Initialize data loader
    loader = FinancialDataLoader()
    companies = loader.load_all_companies()
    
    if not companies:
        print("❌ No financial data found!")
        return
    
    if indicator_name.lower() == 'profitability' and profitability_available:
        calc = ProfitabilityIndicators(loader)
        calc.run_analysis_for_all_companies()
    elif indicator_name.lower() == 'valuation' and valuation_available:
        calc = ValuationIndicators(loader)
        calc.run_analysis_for_all_companies()
    elif indicator_name.lower() == 'growth' and growth_available:
        calc = GrowthIndicators(loader)
        calc.run_analysis_for_all_companies()
    elif indicator_name.lower() == 'liquidity' and liquidity_available:
        calc = LiquidityIndicators(loader)
        calc.run_analysis_for_all_companies()
    else:
        print(f"❌ Indicator '{indicator_name}' not available or not implemented yet")

def show_help():
    """Show help information"""
    help_text = """
🔍 FUNDAMENTAL ANALYSIS TOOL - HELP
=" * 50

USAGE:
    python run_all_indicators.py [command] [options]

COMMANDS:
    (no command)    Run all available indicators
    profitability   Run only profitability analysis
    valuation       Run only valuation analysis  
    growth          Run only growth analysis
    liquidity       Run only liquidity analysis
    help            Show this help message

EXAMPLES:
    python run_all_indicators.py
    python run_all_indicators.py profitability
    python run_all_indicators.py valuation

OUTPUT:
    Results are saved in the 'outputs/' directory with subdirectories for each indicator type.
    Each analysis generates:
    - CSV files with detailed metrics
    - JSON files with structured data
    - Summary text files with key insights
    
REQUIREMENTS:
    - Financial data must be available in '../financial_reports/data/'
    - Python packages: pandas, numpy
    - Sufficient disk space for output files

For more information, see README.md
"""
    print(help_text)

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'help':
            show_help()
        elif command in ['profitability', 'valuation', 'growth', 'liquidity']:
            run_specific_indicator(command)
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python run_all_indicators.py help' for usage information")
    else:
        # Run all indicators
        run_all_fundamental_analysis()

if __name__ == "__main__":
    main() 