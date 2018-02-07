import React, { Component } from 'react';
import { Scrollbars } from 'react-custom-scrollbars';
import Cookies from 'js-cookie';

export default class ImageCollection extends Component {

  constructor(props) {
    super(props);
    this.state = {
      imageUrls: ['http://naturaldogguide.com/wp-content/uploads/2016/10/Ring-Worm-in-Dogs.jpg','http://purrfectcatbreeds.com/wp-content/uploads/2014/06/Chartreux4.jpg','https://bransbyhorses.co.uk/app/uploads/2016/03/Sophie.jpg','https://upload.wikimedia.org/wikipedia/commons/7/71/2010-kodiak-bear-1.jpg'],
      selected: 0
    };
  }

  select(index) {
    this.setState({selected:index})
  }

  saveImage(img) {
    const urls = this.state.imageUrls;
    const name = img.name;
    const collection = this;
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
        response.json().then(function(data) {
          urls.push('http://127.0.0.1:8000/media/images/' + data.filename);
          collection.setState({imageUrls: urls})
        })

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
      <div style={{width: '250px', height: '810px', backgroundColor: '#BFCCD6'}}>

        <div className="pt-card" style={{backgroundColor: '#5C7080', borderStyle:'solid', borderWidth:'2px', borderColor:'#394B59'}}>
        <h2 style={{color:'#FFFFFF', paddingBottom:'5px'}}>Test Images</h2>
        <label style={{width: '115px'}}className="pt-file-upload pt-button pt-icon-add ">
        Add Image
          <input onChange={(event) => this.saveImage(event.target.files[0])} type="file"/>
        </label>
        </div>
        <Scrollbars style={{ height: '700px' }}>
          <ul style={{listStyleType: 'none', padding: 0, margin: 0}}>
           {
             this.state.imageUrls.map(function(url, index){
           return <li style={{padding: '5px 0px 5px 0px'}}><img src={url} onClick={() => collection.setState({selected: index})} style={(index == selected) ? selectedStyle : imageStyle} /></li>;
                   })}
           </ul>
        </Scrollbars>
      </div>
    );
  }
}
