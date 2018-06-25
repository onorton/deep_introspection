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
    The original class predicted for this image was {this.props.results.originalClass}.
    <br/>
    <h5>Largest Change in Confidence</h5>
    <p>After 10 samples, the features that are occluded to produce the largest change in probability for {this.props.results.originalClass} are {this.props.results.lc.features +'.'}</p>
    <img src={this.occlusionsToUrl(this.props.results.lc.features)} style={{width:'50%', borderStyle:"solid", borderColor:"#10161A",position:'relative', top: 0, left: 0}}/>
    <Predictions style={predictionsStyle} predictions={this.props.results.lc.predictions}/>
    <br/>

    <h5>Most Important Feature</h5>
    <p>The single feature that produces the largest change in probability for {this.props.results.originalClass} is feature {this.props.results.mi.feature}.</p>
    <img src={this.occlusionsToUrl([this.props.results.mi.feature])} style={{width:'50%', borderStyle:"solid", borderColor:"#10161A",position:'relative', top: 0, left: 0}}/>
    <Predictions style={predictionsStyle} predictions={this.props.results.mi.predictions}/>
    <br/>

    <h5>Minimal Features Required</h5>
    <p>The minimal features required to still predict {this.props.results.originalClass} are {(this.props.results.mfRequired.features.length > 0) ? this.props.results.mfRequired.features + '.' : 'none of those found.'}</p>
    <img src={this.occlusionsToUrl(difference(this.props.features, this.props.results.mfRequired.features))} style={{width:'50%', borderStyle:"solid", borderColor:"#10161A",position:'relative', top: 0, left: 0}}/>
    <Predictions style={predictionsStyle} predictions={this.props.results.mfRequired.predictions}/>
    <br/>

    <h5>Minimal Features for a Change in Classifation</h5>
    {this.props.results.mfPerturbation.features == [] ? <p>None of the features can be occluded to change the top classification.</p> :
    <div>
    <p>The minimal features that need to be occluded so {this.props.results.originalClass} is not the top class are {this.props.results.mfPerturbation.features + '.'}</p>
    <img src={this.occlusionsToUrl(this.props.results.mfPerturbation.features)} style={{width:'50%', borderStyle:"solid", borderColor:"#10161A",position:'relative', top: 0, left: 0}}/>
    <Predictions style={predictionsStyle} predictions={this.props.results.mfPerturbation.predictions}/>
    <br/>
    </div>
    }
    </div>
    )

  }
}
