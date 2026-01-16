def generate_html(features):
    inputs = ""
    for f in features:
        inputs += f'''
        <label>{f}</label>
        <input type="number" name="{f}" required><br>
        '''

    return f"""
    <html>
    <body>
        <h2>ML Prediction App</h2>
        <form method="post">
            {inputs}
            <button type="submit">Predict</button>
        </form>

        {{% if prediction is not none %}}
            <h3>Prediction: {{ prediction }}</h3>
        {{% endif %}}
    </body>
    </html>
    """
