package com.example.aggregatescankt

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.View
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit

class SplashScreen : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.splash_screen)

        window.decorView.apply {
            // Hide both the navigation bar and the status bar.
            // SYSTEM_UI_FLAG_FULLSCREEN is only available on Android 4.1 and higher, but as
            // a general rule, you should design your app to hide the status bar whenever you
            // hide the navigation bar.
            systemUiVisibility = View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or View.SYSTEM_UI_FLAG_FULLSCREEN
        }

        Executors.newSingleThreadScheduledExecutor().schedule({
            go_activity()
        }, 3, TimeUnit.SECONDS)


    }

    fun go_activity(){
        val i = Intent(this, MainActivity::class.java)
        startActivity(i)
    }
}