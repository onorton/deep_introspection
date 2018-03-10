import React, { Component } from 'react';

export default class OcclusionTool extends Component {

  constructor(props) {
    super(props);
    this.state = {
      features: null
    };
  }
  componentWillReceiveProps() {
    this.fetchFeatures()
  }
  componentDidMount() {
    this.fetchFeatures()
  }

  fetchFeatures() {
    const tool = this
    fetch('http://127.0.0.1:8000/features/' + this.props.testModel.id + '/' + this.props.testImage.id, {
      method: 'GET',
      headers: {
          "Content-Type": "application/json"
      }
    }).then(function(response) {
      if (response.status == 200) {
        response.json().then(function(data) {
          const features = data.features.map(function(feature) {return {feature: feature, active: true}})
          console.log(features)
          tool.setState({features: features})
        })
      }

    }).catch(function(error) {
      console.log('There has been a problem with your fetch operation: ' + error.message);
    });
  }

  toggle(index) {
    var features = this.state.features
    features[index].active = !features[index].active
    this.setState({features: features})
  }
  render(){
    const tool = this

    return (
    <div className="toolArea">
    <ul style={{listStyleType: 'none', padding: 0, margin: 0, float:'left'}}>
    {(this.state.features != null) ? this.state.features.map(function(feature, index) {

         const activeFeature = <li style={{padding: '5px 0px 5px 0px'}}><label className="pt-button pt-active pt-intent-primary " onClick={() => tool.toggle(index)}>Feature {feature.feature}</label></li>
         const inactiveFeature =  <li style={{padding: '5px 0px 5px 0px'}}><label className="pt-button pt-intent-primary" onClick={() => tool.toggle(index)}>Feature {feature.feature}</label></li>
        return (feature.active) ? activeFeature : inactiveFeature
    }): <div/>}
    </ul>
    {(this.props.testImage != undefined) ? <img src={this.props.testImage.url} style={{maxWidth:300, maxHeight:300, float:"right", marginRight:20, borderStyle:"solid", borderColor:"#10161A"}}/> : <div/>}
    </div>
    )
  }
}
