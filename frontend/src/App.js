import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import styles from '../node_modules/@blueprintjs/core/dist/blueprint.css';

import ImageCollection from './components/ImageCollection'
import UploadModelOverlay from './components/UploadModelOverlay'
import LoginOverlay from './components/LoginOverlay'

import ToolCollection from './components/ToolCollection'

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      testImage: null,
      testModel: null,
      user: null
    };
  }

  onTestModelChanged(model) {
    this.setState({testModel:model})
  }

  onTestImageChanged(img) {
    this.setState({testImage:img})
  }
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h1 className="App-title" style={{color:'#FFFFFF'}}>Deep Introspection</h1>
        </header>
        <LoginOverlay callbackParent={(user) => this.setState({user:user})}/>
        {this.state.user != null ? <UploadModelOverlay callbackParent={(model) => this.onTestModelChanged(model)}/> : <div/>}
        <div className="main-content" style={{position:"absolute", paddingLeft: 260, top: 110, width:"100%" }}>
          {(this.state.testImage != null && this.state.testModel != null) ? <ToolCollection testImage={this.state.testImage} testModel={this.state.testModel}/> : <div/>}
        </div>
        <ImageCollection user={this.state.user} callbackParent={(img) => this.onTestImageChanged(img)} style={{width:250, height:750}}/>
      </div>
    );
  }
}

export default App;
