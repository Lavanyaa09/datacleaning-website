from flask import Flask, render_template, request
import os
import pandas as pd
from sklearn.preprocessing import StandardScaler


app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
CLEANED_FOLDER = os.path.join(os.path.dirname(__file__), 'cleaned')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CLEANED_FOLDER'] = CLEANED_FOLDER


def standardize_data(df):
    try:
        # Select only numerical columns for standardization
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns

        # Standardize numerical columns using Z-score
        scaler = StandardScaler()
        df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

        return df
    except Exception as e:
        print(f"Error standardizing data: {e}")
        return None


def clean_data(input_path, output_path):
    try:
        df = pd.read_excel(input_path)


        # Data cleaning operations...
        df.dropna(inplace=True)
        df.fillna('NA', inplace=True)  # Fill empty gaps with 'NA'
        df.interpolate(inplace=True)
       #handling duplicate data
        df.drop_duplicates(inplace=True)

        # Use absolute path for saving cleaned file
        output_path = os.path.join(app.config['CLEANED_FOLDER'], os.path.basename(output_path))
        df.to_excel(output_path, index=False)

        return df  # Return cleaned DataFrame
    except Exception as e:
        print(f"Error cleaning data: {e}")
        return None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', message='No file part')

    file = request.files['file']

    if file.filename == '':
        return render_template('index.html', message='No selected file')

    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        cleaned_filename = file.filename.replace('.', '_cleaned.')
        cleaned_filepath = os.path.join(app.config['CLEANED_FOLDER'], cleaned_filename)

        cleaned_data = clean_data(filename, cleaned_filepath)

        if cleaned_data is not None:
            # Pass the cleaned data to the template
            return render_template('index.html', message='File uploaded and cleaned successfully', cleaned_data=cleaned_data.to_html())
        else:
            return render_template('index.html', message='Error cleaning data. Please check your file.')

if __name__ == '__main__':
    app.run(debug=True)