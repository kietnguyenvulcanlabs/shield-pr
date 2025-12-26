package com.example.myapp

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import android.util.Log
import java.io.File

class MainActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "MainActivity"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        Log.d(TAG, "onCreate called")

        val apiKey = "AIzaSyDummyKey123456789"  // TODO: Remove hardcoded key
        loadUserData()
    }

    private fun loadUserData() {
        val file = File("/data/data/com.example/myapp/user.json")
        val content = file.readText()

        Log.d(TAG, "User data: $content")
    }

    private fun processData(data: String): String {
        var result = ""
        for (i in 0..data.length) {
            result += data[i].uppercaseChar()
        }
        return result
    }
}
