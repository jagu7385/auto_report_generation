import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import os

def load_and_analyze_data(file_path='sales_data.csv'):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found! Please create sales_data.csv in this folder.")

    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Revenue'] = df['Quantity'] * df['Unit_Price']

    total_revenue = df['Revenue'].sum()
    total_orders = len(df)
    avg_order_value = df['Revenue'].mean()
    top_products = df.groupby('Product')['Revenue'].sum().sort_values(ascending=False)

    df['Month'] = df['Date'].dt.strftime('%Y-%m')
    monthly_revenue = df.groupby('Month')['Revenue'].sum()

    print("✅ Data loaded successfully!")
    print(f"Total Revenue     : Rs. {total_revenue:,.2f}")
    print(f"Total Orders      : {total_orders}")
    print(f"Avg Order Value   : Rs. {avg_order_value:,.2f}")

    return df, {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'top_products': top_products,
        'monthly_revenue': monthly_revenue
    }

def generate_charts(df, analysis):
    # Revenue by Product
    plt.figure(figsize=(8, 5))
    analysis['top_products'].plot(kind='bar', color='skyblue')
    plt.title('Revenue by Product')
    plt.ylabel('Revenue (Rs.)')
    plt.xlabel('Product')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('revenue_by_product.png', dpi=200)
    plt.close()

    # Monthly Trend
    plt.figure(figsize=(8, 5))
    analysis['monthly_revenue'].plot(kind='line', marker='o', color='green')
    plt.title('Monthly Revenue Trend')
    plt.ylabel('Revenue (Rs.)')
    plt.xlabel('Month')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('monthly_trend.png', dpi=200)
    plt.close()

    print("✅ Charts generated successfully.")

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Sales Performance Report', ln=True, align='C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f'Generated on: {datetime.now().strftime("%d %B %Y at %H:%M")}', ln=True, align='C')
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 80, 160)
        self.cell(0, 10, title, ln=True)
        self.ln(4)
        self.set_text_color(0, 0, 0)

    def chapter_body(self, text):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 8, text)
        self.ln(5)

def create_pdf_report(analysis, df, output_file='Sales_Report.pdf'):
    pdf = PDFReport()
    pdf.add_page()

    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 15, 'MONTHLY SALES ANALYSIS REPORT', ln=True, align='C')
    pdf.ln(10)

    # Executive Summary
    pdf.chapter_title('Executive Summary')
    summary = f"""
Total Revenue Generated      : Rs. {analysis['total_revenue']:,.2f}
Total Number of Orders       : {analysis['total_orders']}
Average Order Value          : Rs. {analysis['avg_order_value']:,.2f}
Report Period                : January - April 2026
Generated On                 : {datetime.now().strftime('%d %B %Y')}
    """
    pdf.chapter_body(summary)

    # Top Products (using safe '-' instead of bullet)
    pdf.chapter_title('Top Performing Products')
    pdf.set_font('Arial', '', 11)
    for product, revenue in analysis['top_products'].items():
        pdf.cell(0, 8, f"- {product:<15} : Rs. {revenue:,.2f}", ln=True)
    pdf.ln(8)

    # Charts
    pdf.chapter_title('Revenue by Product')
    pdf.image('revenue_by_product.png', x=15, w=170)
    pdf.ln(12)

    pdf.chapter_title('Monthly Revenue Trend')
    pdf.image('monthly_trend.png', x=15, w=170)
    pdf.ln(12)

    # Detailed Table
    pdf.chapter_title('Detailed Sales Transactions')
    pdf.set_font('Arial', 'B', 10)
    col_widths = [28, 45, 20, 35, 40]
    headers = ['Date', 'Product', 'Qty', 'Unit Price', 'Revenue']

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align='C')
    pdf.ln()

    pdf.set_font('Arial', '', 9)
    for _, row in df.iterrows():
        pdf.cell(col_widths[0], 8, str(row['Date'].date()), border=1)
        pdf.cell(col_widths[1], 8, str(row['Product']), border=1)
        pdf.cell(col_widths[2], 8, str(row['Quantity']), border=1, align='C')
        pdf.cell(col_widths[3], 8, f"Rs. {row['Unit_Price']:,.0f}", border=1, align='R')
        pdf.cell(col_widths[4], 8, f"Rs. {row['Revenue']:,.2f}", border=1, align='R')
        pdf.ln()

    pdf.output(output_file)
    print(f"\n✅ PDF Report successfully created: {output_file}")

if __name__ == "__main__":
    try:
        df, analysis = load_and_analyze_data('sales_data.csv')
        generate_charts(df, analysis)
        create_pdf_report(analysis, df, 'Sales_Report.pdf')

        print("\n🎉 All done! Open 'Sales_Report.pdf' to view your professional report.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("   Make sure 'sales_data.csv' exists in the current folder.")