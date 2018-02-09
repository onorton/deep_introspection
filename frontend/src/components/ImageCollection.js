import React, { Component } from 'react';
import { Scrollbars } from 'react-custom-scrollbars';
import Cookies from 'js-cookie';
import { Position, Toaster, Intent } from "@blueprintjs/core";
import {MainToaster} from '../MainToaster'

export default class ImageCollection extends Component {

  constructor(props) {
    super(props);
    this.state = {
      imageUrls: [],
      selected: 0
    };
  }

  componentWillMount() {
    const collection = this
    fetch('http://127.0.0.1:8000/uploadImage/', {
      method: 'GET',
      headers: {
          "Content-Type": "application/json"
      }
    }).then(function(response) {
      if (response.status == 200) {
        response.json().then(function(data) {
          collection.setState({imageUrls: data.urls})
          collection.props.callbackParent(data.urls[0])

        })
      }

    }).catch(function(error) {
      console.log('There has been a problem with your fetch operation: ' + error.message);
    });
  }



  select(index) {
    console.log('sup')
    this.props.callbackParent(this.state.imageUrls[index])
    this.setState({selected:index})
  }

  isImage(filename) {
    var parts = filename.split('.');
    const ext = parts[parts.length - 1];
    switch (ext.toLowerCase()) {
        case 'jpg':
        case 'gif':
        case 'bmp':
        case 'png':
            //etc
            return true;
    }
    return false;
  }

  saveImage(img) {
    const urls = this.state.imageUrls;
    const name = img.name;
    const collection = this;
    // Check that file has image extension, alert user if not
    if (!this.isImage(name)) {
      MainToaster.show({ timeout:5000, intent: Intent.DANGER, message: "This file is not an image!" });
      return;
    }
    // Send request to backend
    var reader = new FileReader();
    reader.readAsDataURL(img);
    reader.onload = function () {
      // If successfully read image, save on file system

      fetch('http://127.0.0.1:8000/uploadImage/', {
        method: 'POST',
        body: JSON.stringify({name: name, image: reader.result}),
        headers: {
            "Content-Type": "application/json"
        }
      }).then(function(response) {

        if (response.status == 200) {
          response.json().then(function(data) {
            urls.push('http://127.0.0.1:8000/media/images/' + data.filename);
            collection.setState({imageUrls: urls})
            if(collection.state.imageUrls.length == 1) {
              collection.select(0);
            }

          })
        } else if (response.status == 409) {
          MainToaster.show({ timeout:5000, intent: Intent.WARNING, message: "You have already uploaded this image." });
        }

      }).catch(function(error) {
        console.log('There has been a problem with your fetch operation: ' + error.message);
      });


      };
    reader.onerror = function (error) {
     console.log('Error: ', error);
    };

  }

  render(){
    let collection = this;
    let selected = this.state.selected;
    let imageStyle = {maxHeight: '300px', maxWidth: '90%'}
    let selectedStyle = { outlineColor: '#137CBD', outlineStyle: 'solid', maxHeight: '300px', maxWidth: '90%'}


    return (
      <div style={this.props.style}>
        <div style={{backgroundColor: '#BFCCD6'}}>
        <div className="pt-card" style={{backgroundColor: '#5C7080', borderStyle:'solid', borderWidth:'2px', borderColor:'#394B59'}}>
        <h2 style={{color:'#FFFFFF', paddingBottom:'5px'}}>Test Images</h2>
        <label style={{width: '115px'}}className="pt-file-upload pt-button pt-icon-add ">
        Add Image
          <input  type="file" accept="image/*" onChange={(event) => this.saveImage(event.target.files[0])} type="file"/>
        </label>
        </div>
        {this.state.imageUrls.length == 0 ? (

        <div class="pt-non-ideal-state" style={{height:150, paddingTop:20}}>
        <div class="pt-non-ideal-state-visual pt-non-ideal-state-icon">
        <span class="pt-icon pt-icon-media"></span>
        </div>
        <h4 class="pt-non-ideal-state-title">There are no test images</h4>
        <div class="pt-non-ideal-state-description">
          Add a new image to get started.
          </div>
        </div>) : <div></div>}
        <Scrollbars style={this.props.style}>
          <ul style={{listStyleType: 'none', padding: 0, margin: 0}}>
           {
             this.state.imageUrls.map(function(url, index){
           return <li style={{padding: '5px 0px 5px 0px'}}><img src={url} onClick={() => collection.select(index)} style={(index == selected) ? selectedStyle : imageStyle} /></li>;
                   })}
           </ul>
        </Scrollbars>
      </div>
      </div>
    );
  }
}
