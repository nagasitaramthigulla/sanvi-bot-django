import { Component } from '@angular/core';
import {ApiService} from "./api.service";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  providers: [ApiService],
})
export class AppComponent {
  title = 'frontend';
  names=[];

  constructor(private api:ApiService){
    this.getNames();
  }

  getNames=()=>{
    this.api.getAll().subscribe(data=> {
      this.names = data.data;
    },error =>{

    } )
  }
}
