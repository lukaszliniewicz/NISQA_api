import os
import logging
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from nisqa.NISQA_model import nisqaModel
import tempfile

app = FastAPI()

# Get the current working directory
current_dir = os.getcwd()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/predict")
async def predict(
    audio_file: UploadFile = File(...),
    pretrained_model: str = Form(...),
    ms_channel: int = Form(None),
    output_dir: str = Form(current_dir)
):
    # Save the uploaded audio file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(await audio_file.read())
        temp_path = temp_file.name
    
    # Set up the arguments for prediction
    args = {
        'mode': 'predict_file',
        'pretrained_model': os.path.join(current_dir, 'weights', pretrained_model),
        'deg': temp_path,
        'ms_channel': ms_channel,
        'output_dir': output_dir,
        'tr_bs_val': 1,
        'tr_num_workers': 0
    }
    
    try:
        # Load the pretrained NISQA model
        nisqa = nisqaModel(args)
        
        # Predict the quality score using NISQA
        nisqa.predict()
        
        # Get the predicted scores from the output file
        output_file = os.path.join(output_dir, 'NISQA_results.csv')
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                # Skip the header row
                header = next(f).strip().split(',')
                result = f.readline().strip().split(',')
                scores = dict(zip(header, result))
            os.unlink(output_file)  # Remove the output file after reading the scores
            
            if pretrained_model == 'nisqa_tts.tar':
                return {"mos": float(scores['mos_pred']), "model": scores['model']}
            else:
                return {
                    "mos": float(scores['mos_pred']),
                    "noi": float(scores['noi_pred']),
                    "dis": float(scores['dis_pred']),
                    "col": float(scores['col_pred']),
                    "loud": float(scores['loud_pred']),
                    "model": scores['model']
                }
        else:
            raise FileNotFoundError(f"Output file not found: {output_file}")
    
    except Exception as e:
        logger.exception("Error during prediction")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
    
    finally:
        # Clean up temporary files
        os.unlink(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8356)
