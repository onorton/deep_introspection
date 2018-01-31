import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import ImageCollection from './panels/ImageCollection'
class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h1 className="App-title">Deep Introspection</h1>
        </header>
        <ImageCollection></ImageCollection>

      </div>
    );
  }
}

export default App;
