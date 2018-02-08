import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import styles from '../node_modules/@blueprintjs/core/dist/blueprint.css';
import { Tab2, Tabs2 } from "@blueprintjs/core";

import ImageCollection from './components/ImageCollection'
import UploadModelOverlay from './components/UploadModelOverlay'
import ToolCollection from './components/ToolCollection'

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h1 className="App-title" style={{color:'#FFFFFF'}}>Deep Introspection</h1>
        </header>
        <ImageCollection style={{width:250, height:750}}/>
        <div className="main-content" style={{position:"relative", paddingLeft: 260, bottom: 745}}>
          <ToolCollection/>
        </div>
      </div>
    );
  }
}

export default App;
