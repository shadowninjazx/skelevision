<!-- PROJECT LOGO -->
<br />
<div align="center">

  <h3 align="center">Skelevision</h3>

  <p align="center">
    A deep neural network for high throughput measurement of functional traits on museum skeletal specimens.
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

We adapt recent deep nerual network approaches in computer vision to enable high throughput measurement of functional traits on museum skeletal specimens.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

It is recommended to set up virtualenv or conda prior to installation. You can install Python3 virtualenv like this. 

```
python3.8 -m venv DESIRED_DIRECTORY
```

### Prerequisites

Skelevision requires installation of Detectron2 [https://github.com/facebookresearch/detectron2] and compatible PyTorch [https://pytorch.org/get-started/locally/] version. Please keep in mind that using GPU requires compatible cuda version. 

### Installation

Install the remaining requirements in requirements.txt. 

```
pip install -r requirements.txt
```


<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

We provide sample training code, prediction code, and also a pretrained model to for demo. 

### Demo
For a quick demo, checkout demo.ipynb. 

### Training from Scratch
To train from scratch, simply load annotations in COCO format. We provide sample annotation in the dataset folder. The input arguments are explained here:

1. -a path to annotation in COCO JSON
2. -d path to the directory containing the training images
3. -o output directory (default:checkpoint)
4. -i number of training iterations (default:6000)
5. -g the gpu id to use for training (default:0 or cpu) 

```
python train.py -a dataset/oct_2021_annotation.json -d ../bones/_datasets/skeletor_dataset/full -i 100
```

### Predicting Length on New Images
You can run predictions on new images with our pretrained model or a model you trained yourself. Currently, the prediction code is calibrated for image resolution of (1368, 912) with the setup in Skelevision. Different images will require modification to the camera calibration. 

1. -c path to checkpoint directory for trained model
2. -d path to the directory containing the training images
3. -o output directory (default:output)
4. -a path to annotation in COCO JSON format (required for visualization)
5. -g the gpu id to use for training (default:0 or cpu) 

```
python predict.py -c checkpoint -d test_folder -a dataset/oct_2021_annotation.json
```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->
## License

Coming soon. 

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Coming soon. 

<p align="right">(<a href="#top">back to top</a>)</p>



Create with [README Page Template](https://github.com/othneildrew/Best-README-Template/blob/master/README.md)




<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/shadowninjazx/skelevision/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/shadowninjazx/skelevision/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/shadowninjazx/skelevision/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/shadowninjazx/skelevision/issues
[product-screenshot]: images/screenshot.png
