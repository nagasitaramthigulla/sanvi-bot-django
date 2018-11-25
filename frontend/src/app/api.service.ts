import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {Observable} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  baseUrl = "https://localhost:8000";

  httpHeaders = new HttpHeaders({'Content-Type':'application/json'});

  constructor(private http:HttpClient) {  }

  getAll():Observable<any>{
      return this.http.get(this.baseUrl+"/names/",{headers:this.httpHeaders});
    }
}
