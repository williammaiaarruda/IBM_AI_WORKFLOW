import os
from datetime import datetime
from model import model_predict, model_load


def main():   
    print("LOADING MODELS")
    production_data_dir = os.path.join("data", "cs-production")
    all_data, all_models = model_load(data_dir=production_data_dir)
    
    print("... models loaded: ",",".join(all_models.keys()))
    
    count = 0

    for country in all_data.keys():
        
        if all_data[country]['X'].shape[0] > 0:
            
            for date in all_data[country]['dates']:
                
                dt = datetime.strptime(date, '%Y-%m-%d')
                
                query = {'country': country,
                         'year': str(dt.year),
                         'month': str(dt.month),
                         'day': str(dt.day)
                        }

                # input checks
                if country not in all_models.keys():
                    result = "ERROR (model_predict) - model for country '{}' could not be found".format(country)
                else:
                    result = model_predict(query, data=all_data[country], model=all_models[country], test=True)
   
                count += 1
                
                print('result[', count, ']: ', result)

    
    print("model test predict complete.")


if __name__ == "__main__":

    main()
