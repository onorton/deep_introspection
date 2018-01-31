import React, { Component } from 'react';
import { Scrollbars } from 'react-custom-scrollbars';

export default class ImageCollection extends Component {

  constructor(props) {
    super(props);
    this.state = {
      imageUrls: ['http://naturaldogguide.com/wp-content/uploads/2016/10/Ring-Worm-in-Dogs.jpg','http://purrfectcatbreeds.com/wp-content/uploads/2014/06/Chartreux4.jpg','https://bransbyhorses.co.uk/app/uploads/2016/03/Sophie.jpg'],
      selected: 0
    };
  }

  select(index) {
    this.setState({selected:index})
  }

  render(){
    let collection = this;
    let selected = this.state.selected;
    let imageStyle = {maxHeight: '300px', maxWidth: '90%'}
    let selectedStyle = { outlineColor: '#005ce6', outlineStyle: 'solid', maxHeight: '300px', maxWidth: '90%'}

    return (
      <div style={{width: '300px', height: '100%', backgroundColor: '#CCCCCC'}}>
        <Scrollbars style={{ height: 780 }}>
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
