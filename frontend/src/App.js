import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import styles from '../node_modules/@blueprintjs/core/dist/blueprint.css';

import ImageCollection from './components/ImageCollection'
import UploadModelOverlay from './components/UploadModelOverlay'

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h1 className="App-title" style={{color:'#FFFFFF'}}>Deep Introspection</h1>
        </header>
        <UploadModelOverlay/>
        <ImageCollection></ImageCollection>

      </div>
    );
  }
}

export default App;
