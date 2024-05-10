import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set(style='darkgrid')


csv_path = '/Users/connerjordan/Downloads/export.csv'
df = pd.read_csv(csv_path)


# parse single column of JSON, concat back into other columns
def parse_json(raw_str):
    try:
        return json.loads(raw_str)
    except (TypeError, ValueError):
        return {}

parsed_data = df['raw_data'].apply(parse_json)
parsed_df = pd.json_normalize(parsed_data)
final_df = pd.concat([df[['id', 'hostname', 'ip_address', 'timestamp']], parsed_df], axis=1)

print(final_df.columns)

#compare to postgres calc:
#fanclub_data=# SELECT AVG((raw_data->'internet_speed'->>'download_speed_mbps')::NUMERIC) AS avg_download_speed
#FROM raw_data;
#  avg_download_speed  
#----------------------
# 136.0202823399997685
#(1 row)

mean_download_speed = final_df['internet_speed.download_speed_mbps'].mean()
print(f"Mean Download Speed: {mean_download_speed} Mbps")

#heatmap
numeric_columns = final_df.select_dtypes(include='number')
corr = numeric_columns.corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
plt.title("Correlation Heatmap")
plt.show()

#internet speed over time
plt.figure(figsize=(10, 6))
plt.plot(final_df['timestamp'], final_df['internet_speed.upload_speed_mbps'], label='Upload Speed (Mbps)', color='green')
plt.plot(final_df['timestamp'], final_df['internet_speed.download_speed_mbps'], label='Download Speed (Mbps)', color='red')
plt.xticks(rotation=45)
plt.xlabel('Timestamp')
plt.ylabel('Speed (Mbps)')
plt.title('Internet Speeds Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

#network traffic
plt.figure(figsize=(10, 6))
plt.plot(final_df['timestamp'], final_df['network.bytes_recv'], label='Bytes Received', color='blue')
plt.plot(final_df['timestamp'], final_df['network.bytes_sent'], label='Bytes Sent', color='orange')
plt.xticks(rotation=45)
plt.xlabel('Timestamp')
plt.ylabel('Bytes')
plt.title('Network Traffic Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

#memory usage
memory_data = final_df[['timestamp', 'memory.used', 'memory.total']].copy()
memory_data['memory.free'] = memory_data['memory.total'] - memory_data['memory.used']

memory_data.plot(
    x='timestamp',
    kind='bar',
    stacked=True,
    figsize=(12, 6),
    title='Memory Usage Over Time'
)
plt.xlabel('Timestamp')
plt.ylabel('Memory (Bytes)')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.tight_layout()
plt.show()

#cpu usage
plt.figure(figsize=(10, 6))
plt.plot(final_df['timestamp'], final_df['cpu_usage'], label='CPU Usage (%)')
plt.xticks(rotation=45)
plt.xlabel('Timestamp')
plt.ylabel('CPU Usage (%)')
plt.title('CPU Usage Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# box plot
plt.figure(figsize=(8, 6))
sns.boxplot(data=final_df[['internet_speed.download_speed_mbps', 'internet_speed.upload_speed_mbps']])
plt.title("Box Plot of Internet Speeds")
plt.xlabel("Speed Type")
plt.ylabel("Speed (Mbps)")
plt.xticks([0, 1], ['Download Speed', 'Upload Speed'])
plt.show()

#time-series
fig, axes = plt.subplots(3, 1, figsize=(12, 12))
sns.lineplot(x='timestamp', y='memory.used', data=final_df, ax=axes[0], color='blue')
axes[0].set_title("Memory Usage Over Time")
axes[0].set_xlabel("Timestamp")
axes[0].set_ylabel("Memory Used (Bytes)")

sns.lineplot(x='timestamp', y='network.bytes_recv', data=final_df, ax=axes[1], color='green')
sns.lineplot(x='timestamp', y='network.bytes_sent', data=final_df, ax=axes[1], color='orange')
axes[1].set_title("Network Bytes Sent and Received Over Time")
axes[1].set_xlabel("Timestamp")
axes[1].set_ylabel("Bytes")
axes[1].legend(['Bytes Received', 'Bytes Sent'])

sns.lineplot(x='timestamp', y='internet_speed.download_speed_mbps', data=final_df, ax=axes[2], color='red')
sns.lineplot(x='timestamp', y='internet_speed.upload_speed_mbps', data=final_df, ax=axes[2], color='purple')
axes[2].set_title("Internet Download and Upload Speeds Over Time")
axes[2].set_xlabel("Timestamp")
axes[2].set_ylabel("Speed (Mbps)")
axes[2].legend(['Download Speed', 'Upload Speed'])

plt.tight_layout()
plt.show()

#pair plot
sns.pairplot(final_df[['cpu_usage', 'memory.used', 'network.bytes_recv', 'network.bytes_sent', 'internet_speed.download_speed_mbps']])
plt.show()
