package com.example.securecharger;

import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;
import java.util.Iterator;

public class MainActivity extends AppCompatActivity {
    Button button;
    EditText charging_cost;
    TextView display_balance;
    Button get_button;
    EditText get_username;
    DatabaseReference user_data;
    EditText username_input;

    /* access modifiers changed from: protected */
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView((int) C0338R.layout.activity_main);
        this.username_input = (EditText) findViewById(C0338R.C0340id.editText);
        this.charging_cost = (EditText) findViewById(C0338R.C0340id.editText2);
        this.get_username = (EditText) findViewById(C0338R.C0340id.editText3);
        this.button = (Button) findViewById(C0338R.C0340id.button);
        this.get_button = (Button) findViewById(C0338R.C0340id.button2);
        this.display_balance = (TextView) findViewById(C0338R.C0340id.textView2);
        this.user_data = FirebaseDatabase.getInstance().getReference("Users");
        this.get_button.setOnClickListener(new OnClickListener() {
            public void onClick(View v) {
                final String get_user = MainActivity.this.get_username.getText().toString().trim();
                MainActivity.this.user_data.addValueEventListener(new ValueEventListener() {
                    public void onDataChange(DataSnapshot dataSnapshot) {
                        if (dataSnapshot.exists()) {
                            boolean user_found = false;
                            Iterator it = dataSnapshot.getChildren().iterator();
                            while (true) {
                                if (!it.hasNext()) {
                                    break;
                                }
                                DataSnapshot get_users = (DataSnapshot) it.next();
                                if (get_user.equals(get_users.getKey())) {
                                    user_found = true;
                                    String charge_val = ((User_info) get_users.getValue(User_info.class)).chargingCost;
                                    TextView textView = MainActivity.this.display_balance;
                                    StringBuilder sb = new StringBuilder();
                                    sb.append("Your current balance is ");
                                    sb.append(charge_val);
                                    textView.setText(sb.toString());
                                    break;
                                }
                            }
                            if (!user_found) {
                                Toast.makeText(MainActivity.this, "User not found. Please try again.", 1).show();
                            }
                            MainActivity.this.user_data.removeEventListener((ValueEventListener) this);
                        }
                    }

                    public void onCancelled(DatabaseError databaseError) {
                    }
                });
            }
        });
        this.button.setOnClickListener(new OnClickListener() {
            public void onClick(View v) {
                final String username = MainActivity.this.username_input.getText().toString().trim();
                final String[] charge_cost = {MainActivity.this.charging_cost.getText().toString().trim()};
                MainActivity.this.user_data.addValueEventListener(new ValueEventListener() {
                    public void onDataChange(DataSnapshot dataSnapshot) {
                        boolean user_exists = false;
                        if (dataSnapshot.exists()) {
                            for (DataSnapshot userSnapshot : dataSnapshot.getChildren()) {
                                if (username.equals(userSnapshot.getKey())) {
                                    user_exists = true;
                                    charge_cost[0] = Integer.toString(Integer.parseInt(((User_info) userSnapshot.getValue(User_info.class)).chargingCost) + Integer.parseInt(charge_cost[0]));
                                }
                            }
                            if (user_exists) {
                                User_info user_info = new User_info(charge_cost[0], Boolean.valueOf(false));
                                MainActivity.this.user_data.removeEventListener((ValueEventListener) this);
                                MainActivity.this.user_data.child(username).setValue(user_info);
                                return;
                            }
                            MainActivity.this.user_data.child(username).setValue(new User_info(charge_cost[0], Boolean.valueOf(false)));
                            MainActivity.this.user_data.removeEventListener((ValueEventListener) this);
                        }
                    }

                    public void onCancelled(DatabaseError databaseError) {
                    }
                });
                String str = "";
                MainActivity.this.username_input.setText(str);
                MainActivity.this.charging_cost.setText(str);
                Toast.makeText(MainActivity.this, "Token Bought Successfully", 1).show();
            }
        });
    }
}
