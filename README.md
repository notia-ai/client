<div align="center">
<img src="https://raw.githubusercontent.com/notia-ai/client/master/resources/imgs/notia-gh-logo.png" width=60%/><br/>  
</div>
<p align="center">
<a href="https://pypi.org/project/notia/">
    <img alt="PyPi Release" src="https://img.shields.io/pypi/v/notia">
</a> 
</p>


---

Use Notia to supercharge your models with the latest training data.

-   Browse over 500 datasets from top companies and institutions.
-   Directly integrates with Jupyter for easy sharing and distribution.
-   Focus on the data science. Spend less time manually scraping and cleaning data.
-   Reproduce any experiment without any need to load up Google Drive, Dropbox
    etc.

## ⚡️ Quick Install

To install notia, simply:

```bash
pip install notia
```

## Usage

```python
import notia
notia.login()

notia.search("WikiQA")

train_df = notia.load_dataset("XXXXX", split="train")
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
