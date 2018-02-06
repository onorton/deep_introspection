import React, { Component } from 'react';
import { Scrollbars } from 'react-custom-scrollbars';
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
    const imageUrls = this.state.imageUrls;
    const name = img.name;
    // Send request to backend
    var reader = new FileReader();
    reader.readAsDataURL(img);
    reader.onload = function () {
      // If successfully read image, save on file system
      const url = 'http://localhost:8000/images/'+name;
      // Add save image url to imageUrls
      imageUrls.push(url);
      var req = new XMLHttpRequest(),
        path = "http://localhost:8000/uploadImage/" + name,
        data = JSON.stringify({image: reader.result});
        req.onreadystatechange = function(err) {
            if (req.readyState == 4 && req.status == 200){
                console.log(req.responseText);
            } else {
                console.log(err);
            }
        };
        // Set the content type of the request to json since that's what's being sent
        req.open("POST", path, true);
        req.setRequestHeader('Content-Type', 'application/json');
        req.send(data);
      };
    reader.onerror = function (error) {
     console.log('Error: ', error);
    };
    this.setState({imageUrls: imageUrls})

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
