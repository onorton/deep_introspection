import React, { Component } from 'react';
import Predictions from './Predictions'

function difference(allFeatures, features) {
  return allFeatures.filter((feature) => features.indexOf(feature) < 0)
}

export default class OcclusionResult extends Component {

  occlusionsToUrl(features) {
    const url = 'media/features/model_' + this.props.testModel.id + '_image_' + this.props.testImage.id + '_' + features.join('_') + '.jpg'
    return url

  }

  render(){
    const predictionsStyle = {width:400, marginLeft:'auto',marginRight:'auto'}
    return (
    <div style={this.props.style}>
    <h4>Occlusion Analysis</h4>
    The original class predicted for this image was {this.props.originalClass}.

    <h5>Largest Change in Prediction</h5>
    The features that are occluded to produce the largest change in probability for {this.props.originalClass} are {this.props.lc.features +'.'}
    <img src={this.occlusionsToUrl(this.props.lc.features)} style={{width:'50%', borderStyle:"solid", borderColor:"#10161A",position:'relative', top: 0, left: 0}}/>
    <Predictions style={predictionsStyle} predictions={this.props.lc.predictions}/>

    <h5>Most Important Feature</h5>
    The single feature that produces the largest change in probability for {this.props.originalClass} is feature {this.props.mi.feature}.
    <img src={this.occlusionsToUrl([this.props.mi.feature])} style={{width:'50%', borderStyle:"solid", borderColor:"#10161A",position:'relative', top: 0, left: 0}}/>
    <Predictions style={predictionsStyle} predictions={this.props.mi.predictions}/>

    <h5>Minimal Features Required</h5>
    The minimal features required to still predict {this.props.originalClass} are {(this.props.mfRequired.features.length > 0) ? this.props.mfRequired.features + '.' : 'none of those found.'}
    <img src={this.occlusionsToUrl(difference(this.props.features, this.props.mfRequired.features))} style={{width:'50%', borderStyle:"solid", borderColor:"#10161A",position:'relative', top: 0, left: 0}}/>
    <Predictions style={predictionsStyle} predictions={this.props.mfRequired.predictions}/>

    <h5>Minimal Features Perturbation</h5>
    The minimal features that need to be occluded so {this.props.originalClass} is not predicted are {this.props.mfPerturbation.features + '.'}
    <img src={this.occlusionsToUrl(difference(this.props.features,this.props.mfPerturbation.features))} style={{width:'50%', borderStyle:"solid", borderColor:"#10161A",position:'relative', top: 0, left: 0}}/>
    <Predictions style={predictionsStyle} predictions={this.props.mfPerturbation.predictions}/>
    </div>
    )
  }
}
