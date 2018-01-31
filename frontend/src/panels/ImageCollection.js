import React, { Component } from 'react';
import { Scrollbars } from 'react-custom-scrollbars';

export default class ImageCollection extends Component {

  constructor(props) {
    super(props);
    this.state = {
      imageUrls: [],
      selected: 0
    };
  }


  render(){
    let selected = this.state.selected;
    let imageStyle = {maxHeight: '300px', maxWidth: '90%'}
    let selectedStyle = { borderColor: '#005ce6', borderStyle: 'solid', maxHeight: '300px', maxWidth: '90%'}
    return (
      <div style={{width: '300px', height: '100%', backgroundColor: '#CCCCCC'}}>
        <Scrollbars style={{ height: 780 }}>
         <ul style={{listStyleType: 'none', padding: 0, margin: 0}}>
           {
             this.state.imageUrls.map(function(url, index){
           return <li style={{padding: '5px 0px 5px 0px'}}><img src={url} style={(index == selected) ? selectedStyle : imageStyle} /></li>;
                   })}
           </ul>
        </Scrollbars>
      </div>
    );
  }
}
