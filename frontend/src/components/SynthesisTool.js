import React, { Component } from 'react';
import { Tooltip, Position } from  "@blueprintjs/core";
import Lightbox from 'react-images';
import Gallery from 'react-grid-gallery';

export default class SynthesisTool extends Component {

  constructor(props) {
    super(props);
    this.state = {
      features: [],
      selected: 0,
      hover: null,
      images: [],
      image: null,
    };
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.testImage.id != nextProps.testImage.id || this.props.testModel.id != nextProps.testModel.id) {
      this.setState({image: nextProps.testImage.url, features: [], images: []})
      this.fetchFeatures(nextProps.testModel.id, nextProps.testImage.id)
      this.select(0)
    }
  }
  componentDidMount() {
    this.setState({image: this.props.testImage.url, features: [], images: []})
    this.fetchFeatures(this.props.testModel.id, this.props.testImage.id)
    this.select(0)
  }

  fetchFeatures(model, image) {
    const tool = this
    fetch('/features/' + this.props.testModel.id + '/' + this.props.testImage.id, {
      method: 'GET',
      headers: {
          "Content-Type": "application/json"
      }
    }).then(function(response) {
      if (response.status == 200) {
        response.json().then(function(data) {
          const features = data.features.map(function(feature) {return {feature: feature, active: true}})
          tool.setState({features: features})
        })
      }

    }).catch(function(error) {
      console.log('There has been a problem with your fetch operation: ' + error.message);
    });
  }

  select(index) {
    const tool = this
    this.setState({selected: index})
    fetch('/synthesis/' + this.props.testModel.id + '/' + this.props.testImage.id + '/' + index, {
      method: 'GET',
      headers: {
          "Content-Type": "application/json"
      }
    }).then(function(response) {
      if (response.status == 200) {
        response.json().then(function(data) {
          tool.setState({images: data.images})
        })
      }

    }).catch(function(error) {
      console.log('There has been a problem with your fetch operation: ' + error.message);
    });

  }

  synthesise() {
    const tool = this
    fetch('/synthesis/synthesise/'  + this.props.testModel.id + '/' + this.props.testImage.id + '/' + this.state.selected, {
      method: 'POST',
      headers: {
          "Content-Type": "application/json"
      }
    }).then(function(response) {
      if (response.status == 200) {
        response.json().then(function(data) {
          const images = this.state.images
          images.push(data.image)
          tool.setState({images: images})
        })
      }

    }).catch(function(error) {
      console.log('There has been a problem with your fetch operation: ' + error.message);
    });

  }

  render() {
    const tool = this
    return (
    <div className="toolArea">

      <div className="buttonArea" style={{width:'100%', height:40}}>
        <Tooltip style={{width:200}} content="Synthesising an image will take a couple of hours." position={Position.TOP}>
          <label className="pt-button pt-intent-primary pt-large " onClick={() => {this.synthesise()}}>Synthesise</label>
        </Tooltip>
      </div>

      <ul style={{listStyleType: 'none', padding: 0, marginLeft:10, float:'left'}}>
      {this.state.features.map(function(feature, index) {
           const activeFeature = <li style={{padding: '5px 0px 5px 0px'}}><label className="pt-button pt-active pt-intent-primary " onClick={() => tool.select(index)} onMouseOver={() => tool.setState({hover: index})} onMouseLeave={() => tool.setState({hover: null})}>Feature {feature.feature}</label></li>
           const inactiveFeature =  <li style={{padding: '5px 0px 5px 0px'}}><label className="pt-button pt-intent-primary" onClick={() => tool.select(index)} onMouseOver={() =>  tool.setState({hover: index})} onMouseLeave={() => tool.setState({hover: null})}>Feature {feature.feature}</label></li>
          return (index == tool.state.selected) ? activeFeature : inactiveFeature
      })}
      </ul>


      <div className="image" style={{ float:"right", width: 400, marginRight:20, height:600}}>
        <div style={{position:'relative'}}>
          <img src={this.state.image} style={{width:'100%', borderStyle:"solid", borderColor:"#10161A", zIndex:0,position:'relative', top: 0, left: 0}}/>
          {(this.state.hover != null) ? <img src={'media/features/feature_model_'+ this.props.testModel.id + '_image_' + this.props.testImage.id + '_' + this.state.hover + '.png'} style={{width:'100%', zIndex:1, position:'absolute', top: 0, left: 0}}/> : <div/>}
        </div>
      </div>

      <div style={{marginLeft: 100, marginRight:100}}>
      <Gallery images={this.state.images}/>
      </div>
    </div>
    )
  }
}
