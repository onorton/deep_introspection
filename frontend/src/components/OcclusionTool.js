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
          tool.setState({features: data.features})
        })
      }

    }).catch(function(error) {
      console.log('There has been a problem with your fetch operation: ' + error.message);
    });
  }
  render(){
    return (
    <div className="toolArea">
    {(this.props.testImage != undefined) ? <img src={this.props.testImage.url} style={{maxWidth:300, maxHeight:300, float:"right", marginRight:20, borderStyle:"solid", borderColor:"#10161A"}}/> : <div/>}
    </div>
    )
  }
}
