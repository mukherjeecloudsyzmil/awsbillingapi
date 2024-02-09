from flask import Flask, render_template, request
import boto3

app = Flask(__name__)

@app.route('/billing', methods=['GET', 'POST'])
def get_billing_info():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
    else:
        start_date = request.args.get('start_date', '2024-02-01')
        end_date = request.args.get('end_date', '2024-02-09')

    try:
        # Assuming you have AWS credentials set up properly.
        # If not, you can configure them explicitly here.
        client = boto3.client('ce', region_name='us-east-1')  # 'ce' stands for Cost Explorer
        
        # Get the specified date range's total estimated charges broken down by category
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=['BlendedCost'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ]
        )

        # Extract and format billing information
        cost_breakdown = {}
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                cost_breakdown[group['Keys'][0]] = {
                    'amount': group['Metrics']['BlendedCost']['Amount'],
                    'currency': group['Metrics']['BlendedCost']['Unit']
                }

        return render_template('index.html', cost_breakdown=cost_breakdown)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
